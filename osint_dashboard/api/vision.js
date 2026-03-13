export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') {
    res.statusCode = 200;
    return res.end();
  }

  if (req.method !== 'POST') return res.status(405).json({ error: 'Method Not Allowed' });

  try {
    const { imageUrl } = req.body;
    if (!imageUrl) return res.status(400).json({ error: 'Missing imageUrl' });

    // Fetch image server-side
    const imgReq = await fetch(imageUrl);
    if (!imgReq.ok) {
        return res.status(400).json({ error: 'Failed to fetch image: ' + imgReq.statusText });
    }
    const buf = await imgReq.arrayBuffer();
    const b64 = Buffer.from(buf).toString('base64');

    const prompt = "Analyze this CCTV traffic/surveillance image. Output exactly valid JSON with no markdown formatting. The JSON must contain a 'description' string giving a 1-sentence general summary, and an 'incidents' array of short strings indicating any detected anomalies (e.g., 'Heavy congestion', 'Vehicle accident', 'Pedestrian on road', etc). If normal, the incidents array should be empty.";

    const OLLAMA_API_KEY = process.env.OLLAMA_API_KEY || "dd4800a9c48c431ba4ce6e0b5c63ce64.vtmKnUSIf9XDlvD37EJCiXXb";
    const ollamaPayload = {
      model: "qwen3-vl:235b-instruct",
      messages: [{ role: "user", content: prompt, images: [b64] }],
      stream: false,
      format: "json",
      options: { temperature: 0.1 }
    };

    const resp = await fetch("https://ollama.com/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${OLLAMA_API_KEY}`
      },
      body: JSON.stringify(ollamaPayload)
    });

    const data = await resp.json();
    let content = data.message?.content || "{}";
    
    // strip markdown ticks
    content = content.trim();
    if (content.startsWith("```")) {
       const lines = content.split('\n');
       if (lines[0].startsWith("```")) lines.shift();
       if (lines[lines.length-1].startsWith("```")) lines.pop();
       content = lines.join('\n').trim();
    }

    return res.status(200).json(JSON.parse(content));
  } catch (err) {
    return res.status(500).json({ error: err.message });
  }
}
