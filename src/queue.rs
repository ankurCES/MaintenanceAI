use crate::{UnifiedLog, QueueConfig};
use async_trait::async_trait;
use tracing::{info, error};
use redis::AsyncCommands;
use std::sync::Arc;

#[async_trait]
pub trait MessageQueue: Send + Sync {
    async fn publish_batch(&self, logs: Vec<UnifiedLog>);
}

pub struct StdoutQueue;

#[async_trait]
impl MessageQueue for StdoutQueue {
    async fn publish_batch(&self, logs: Vec<UnifiedLog>) {
        for log in logs {
            info!("STDOUT QUEUE [{}] [{}] : {}", log.source_system, log.level, log.message);
        }
    }
}

pub struct RedisQueue {
    client: redis::Client,
    stream_name: String,
}

impl RedisQueue {
    pub fn new(url: &str, stream_name: &str) -> Result<Self, redis::RedisError> {
        let client = redis::Client::open(url)?;
        Ok(Self {
            client,
            stream_name: stream_name.to_string(),
        })
    }
}

#[async_trait]
impl MessageQueue for RedisQueue {
    async fn publish_batch(&self, logs: Vec<UnifiedLog>) {
        if logs.is_empty() { return; }
        let mut con = match self.client.get_multiplexed_async_connection().await {
            Ok(c) => c,
            Err(e) => { error!("Redis connection failed: {}", e); return; }
        };
        for log in logs {
            if let Ok(json_str) = serde_json::to_string(&log) {
                let _: redis::RedisResult<()> = con.xadd(&self.stream_name, "*", &[("log_data", json_str)]).await;
            }
        }
    }
}

pub struct KafkaQueue {
    client: rskafka::client::Client,
    topic: String,
}

impl KafkaQueue {
    pub async fn new(brokers: Vec<String>, topic: &str) -> Result<Self, rskafka::client::error::Error> {
        let client = rskafka::client::ClientBuilder::new(brokers).build().await?;
        Ok(Self { client, topic: topic.to_string() })
    }
}

#[async_trait]
impl MessageQueue for KafkaQueue {
    async fn publish_batch(&self, logs: Vec<UnifiedLog>) {
        if logs.is_empty() { return; }
        let partition_client = match self.client.partition_client(&self.topic, 0, rskafka::client::partition::UnknownTopicHandling::Retry).await {
            Ok(c) => c,
            Err(e) => { error!("Kafka topic failed: {}", e); return; }
        };
        let mut records = Vec::new();
        for log in logs {
            if let Ok(json_str) = serde_json::to_string(&log) {
                records.push(rskafka::record::Record {
                    key: None,
                    value: Some(json_str.into_bytes()),
                    headers: Default::default(),
                    timestamp: chrono::Utc::now(),
                });
            }
        }
        let _ = partition_client.produce(records, rskafka::client::partition::Compression::NoCompression).await;
    }
}

pub async fn initialize_queue(config: &QueueConfig) -> Arc<dyn MessageQueue> {
    match config.r#type.to_lowercase().as_str() {
        "redis" => {
            let url = config.redis_url.clone().unwrap_or_else(|| "redis://127.0.0.1/".to_string());
            let stream = config.redis_stream.clone().unwrap_or_else(|| "logs".to_string());
            match RedisQueue::new(&url, &stream) {
                Ok(q) => { info!("Redis Message Queue active"); Arc::new(q) },
                Err(_) => { error!("Redis failed. Falling back to STDOUT"); Arc::new(StdoutQueue) }
            }
        },
        "kafka" => {
            let brokers = config.kafka_brokers.clone().unwrap_or_else(|| "localhost:9092".to_string());
            let topic = config.kafka_topic.clone().unwrap_or_else(|| "logs".to_string());
            let broker_list: Vec<String> = brokers.split(',').map(|s| s.trim().to_string()).collect();
            match KafkaQueue::new(broker_list, &topic).await {
                Ok(q) => { info!("Kafka Message Queue active"); Arc::new(q) },
                Err(_) => { error!("Kafka failed. Falling back to STDOUT"); Arc::new(StdoutQueue) }
            }
        },
        _ => {
            info!("Default STDOUT Message Queue active");
            Arc::new(StdoutQueue)
        }
    }
}
