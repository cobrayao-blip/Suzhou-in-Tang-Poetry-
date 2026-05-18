import express from "express";
import path from "path";
import { createServer as createViteServer } from "vite";
import { GoogleGenAI, Type } from "@google/genai";
import * as cheerio from "cheerio";
import dotenv from "dotenv";

dotenv.config();

const app = express();
const PORT = 3000;

app.use(express.json({ limit: '50mb' }));

// Shared Gemini Client
const ai = new GoogleGenAI({ 
  apiKey: process.env.GEMINI_API_KEY || "",
  httpOptions: {
    headers: {
      'User-Agent': 'aistudio-build',
    }
  }
});

// API Routes
app.get("/api/health", (req, res) => {
  res.json({ status: "ok" });
});

/**
 * Enrich a poem with metadata using Gemini
 */
app.post("/api/enrich-poem", async (req, res) => {
  const { title, author, content } = req.body;

  if (!content) {
    return res.status(400).json({ error: "Poem content is required" });
  }

  try {
    const response = await ai.models.generateContent({
      model: "gemini-3-flash-preview",
      contents: `分析以下唐诗，提取其意象、地名、人物关系和苏州元素。
      标题: ${title}
      作者: ${author}
      内容: ${content}`,
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            imagery: {
              type: Type.ARRAY,
              items: { type: Type.STRING },
              description: "诗中的核心意象（如：月、流水、蝉等）"
            },
            places: {
              type: Type.ARRAY,
              items: {
                type: Type.OBJECT,
                properties: {
                  name: { type: Type.STRING },
                  description: { type: Type.STRING },
                  isSuzhouRelated: { type: Type.BOOLEAN }
                },
                required: ["name", "isSuzhouRelated"]
              },
              description: "诗中提及的地名"
            },
            relationships: {
              type: Type.ARRAY,
              items: {
                type: Type.OBJECT,
                properties: {
                  person: { type: Type.STRING },
                  relation: { type: Type.STRING }
                },
                required: ["person", "relation"]
              },
              description: "提及的人物及其与作者的关系"
            },
            suzhouElements: {
              type: Type.ARRAY,
              items: { type: Type.STRING },
              description: "识别出的苏州具体元素（园林、桥梁、巷子等）"
            },
            summary: { type: Type.STRING, description: "诗歌主旨简述" }
          },
          required: ["imagery", "places", "relationships", "suzhouElements", "summary"]
        }
      }
    });

    const metadata = JSON.parse(response.text || "{}");
    res.json(metadata);
  } catch (error: any) {
    console.error("Gemini Error:", error);
    res.status(500).json({ error: error.message });
  }
});

/**
 * Parse an HTML volume of Full Tang Poems
 */
app.post("/api/parse-volume", (req, res) => {
  const { html } = req.body;
  if (!html) return res.status(400).json({ error: "HTML content required" });

  try {
    const $ = cheerio.load(html);
    const poems: any[] = [];
    
    // This is a generic parser for common Tang Poem HTML structures
    // Users might need to adjust this depending on their specific HTML format
    $('div, p').each((_, el) => {
      const text = $(el).text().trim();
      if (text.length > 10) { // Simple heuristic for a poem block
        // In a real app, we would use smarter regex or structure analysis
        poems.push({
          raw: text,
          processed: false
        });
      }
    });

    res.json({ count: poems.length, poems: poems.slice(0, 100) }); // Return first 100 for safety
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// Vite middleware for development
async function startServer() {
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*', (req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on http://localhost:${PORT}`);
  });
}

startServer();
