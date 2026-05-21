require("dotenv").config();

const { Client } = require("@notionhq/client");

const notion = new Client({
  auth: process.env.NOTION_TOKEN,
});

async function createLearningPath() {
  try {

    const response = await notion.pages.create({
      parent: {
        database_id: process.env.NOTION_DATABASE_ID,
      },

      properties: {

        Name: {
          title: [
            {
              text: {
                content: "AI Engineer Roadmap",
              },
            },
          ],
        },

        Difficulty: {
          select: {
            name: "Intermediate",
          },
        },

        Category: {
          select: {
            name: "Artificial Intelligence",
          },
        },

        Content: {
          rich_text: [
            {
              text: {
                content:
                  "Python → Machine Learning → Deep Learning → LLMs → RAG → AI Agents",
              },
            },
          ],
        },

        Status: {
          select: {
            name: "Not Started",
          },
        },
      },
    });

    console.log("SUCCESS!");
    console.log("Page Created:");
    console.log(response.id);

  } catch (error) {
    console.log(error.body || error);
  }
}

createLearningPath();