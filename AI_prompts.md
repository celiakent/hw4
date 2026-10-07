# HW 4 — AI Prompts Log

This file records the prompts I gave to the AI assistant while working on HW 4, organized by problem.

---

## Problem 1: Vibe Code Prompts

**Prompt:**
> Create an ai_prompts.md file in the HW4 folder and keep it updated as we work through the assignment. Give each problem its own section with the problem number and title, at least one prompt I gave you, and any follow-up prompt with a sentence on why I needed it.

**Follow-up prompt:**
> can you also unzip the data.zip in the HW4 folder?

**Why I needed the follow-up:** I needed the assignment's data files (the `campus_customs.db` database and product images) extracted into the HW4 folder so the AI could work with them.

---

## Problem 2: Analyze the Database

**Prompt:**
> Look through data/campus_customs.db and help me understand what's in each table, at least catalogue, inventory, and users. Then start a file at output/harness.md that lists every table and its fields, with one short line per field explaining why it matters for the shop or the chatbot. Set the file up so we can keep adding sections to it later (models, tools, safety, specs).

---

## Problem 3: Build the Campus Customs Website

**Prompt:**
> Build the Campus Customs website. Set up a React + Vite + TypeScript front end with a nav bar at the top linking to Home, Products, About Us, Log in, and Create account. Look at yalebulldogblue.com to get a feel for Campus Customs' style and what they're about, and write the Home and About Us pages in your own words instead of copying their text. On the Products page, show every product from the catalogue as a card with its image (using the image paths in the database), name, price, and a short description. Clicking a card should open a single-item page with a large image on one side and the full details on the other: description, price, and stock by size. Add a floating chat panel in the bottom right corner. It doesn't need to talk to an agent yet, just stub it out so it can call the backend later. Also start a simple FastAPI app in backend/main.py that serves the products and images from the database, which we'll grow into the agent backend later.

---

## Problem 4: Create Account and Login

**Prompt:**
> Now make Create account and Log in actually work. Create account should ask for first name, last name, email, password, and a confirm-password field, and save the new user to the users table. You can use my email (celia.kent@yale.edu) and make up a password but make sure you record it. Log in should take email and password. Store passwords securely so nobody, human or AI, can get the real passwords out of the database. Keep the user logged in across pages, show their name in the nav bar with a Log out option, and give clear errors for things like a wrong password or an email that's already taken. Test it by logging in as the test user that's already in the database and by creating a brand-new account and logging in with it. Then add a section to output/harness.md explaining how auth works: what we store for each user and how passwords are protected.

---

## Problem 5: PydanticAI Agent Backend

**Prompt:**
> Turn the chat stub into a real shop chatbot built as a PydanticAI agent behind FastAPI, wired to the floating chat widget on the site. Keep backend/main.py as the app I run with uvicorn, and split the agent into four files next to it: prompts/prompt.md for the system prompt, agent.py for wiring the agent, tools.py for the tools it can call (looking up products, price, and stock from the database), and models.py for the Pydantic types for chat replies and product cards. Give the agent a Campus Customs voice and basic safety rules in prompt.md, and have it answer honestly about price and stock from the database instead of making things up. The chat response should return both the reply text and any matching product cards so they can show on the page. Use my Portkey API key for the model. Make sure the backend runs from the backend/ folder with `uvicorn main:app --reload --port 8000`, and update output/harness.md with how the front end talks to FastAPI and how the agent is loaded (prompt file plus model).

**Follow-up prompt:**
> Can you set up a place for me to input my Portkey API key?

**Why I needed the follow-up:** The agent needs my Portkey API key to call the model, and I wanted a safe, gitignored place to put it instead of pasting the key into chat or hard-coding it.

---

## Problem 6: Tools — Product Info and Stock

**Prompt:**
> Make sure the agent has solid tools that pull real data from campus_customs.db for a product's description, its price, and how many are in stock (broken down by size when the shopper asks about sizes). The agent must always get these from the database and never make up a price or a quantity, and when a size is out of stock it should say so clearly. Expand prompts/prompt.md so the agent knows to call these tools for any price or stock question, and update the return types in models.py if needed so the tool results are clean and typed. Then in output/harness.md, list each tool and explain which model fields I chose for the lookup results and why.

---

## Problem 7: Chat Search That Updates the Page

**Prompt:**
> Add the feature where asking the chatbot about a kind of item updates the actual website, not just the chat bubble. When someone asks something like "what hoodies do you have?", the agent searches the catalogue and the matching items show up as product cards on the page itself (image, name, price, short info). Keep the backend as a clean contract: the agent returns structured product matches and the front end renders them on the site. Make sure the Problem 3 single-item page still works, so clicking any card (including the ones the chat just added to the page) opens the detail view with the large image and full info. Update prompts/prompt.md and output/harness.md so it's clear how search results travel from the agent to the page.

---

## Problem 8: Customer Memory

**Prompt:**
> Give the chatbot memory and context. When a logged-in shopper chats, save their messages and the agent's replies in the database (the chat_messages table), and when they come back and log in, reload that history into the chat window. The agent should know who it's talking to (the shopper's name and email) so pass that into the agent as dependencies or context. Also pass page context: if someone is on a product page and asks "do you have this in pink?", the agent should know which item they mean. Guests can still chat, but only logged-in users need their history saved. Then document in output/harness.md how chat history is stored, what customer info the agent sees, and how page context is passed.

---

## Problem 9: Usability Improvements

**Prompt:**
> Now that the shop works, make it nicer with 2 front-end and 2 agent/backend usability improvements, and write them up in output/usability.md (what I added and why it helps a Campus Customs shopper or the business). Make sure each one actually shows up in the running app.
>
> For the front-end improvements, take visual and UX cues from acmecups.nz (clean card grid, color names under product titles, clear stock/sale badges, generous whitespace, polished hover effects, a filter/price-range toolbar), but keep the Yale palette — navy blue, grey, and white, not Acme's colors. Two concrete front-end improvements: (1) redesign the product cards Acme-style with the color options listed under the name and a clear stock badge like "Sold out" or "Only a few left", with a subtle hover effect; (2) add a filtering and sorting toolbar on the Products page (price ranges like under $40 / under $60, sort by price, and a color filter) so shoppers can narrow things down the way Acme's price and color collections do.
>
> For the agent/backend, make the agent more accurate and faster/cheaper. Two improvements: (1) validate the agent's output so any product it tries to show is checked against the real catalogue and made-up items are dropped before they reach the page; (2) cache the catalogue in memory so the agent's product lookups don't hit the database on every message, making replies faster and cheaper.

---

## Problem 10: Style the Website

**Prompt:**
> Restyle the whole Campus Customs site to look like acmecups.nz — a clean, editorial, high-end storefront — while keeping the Yale palette (navy blue, grey, white). Take as many design cues from that site as you can: sharp and minimal (square 90° corners, thin 1px borders, no tinted backgrounds or soft shadows, clean white with generous whitespace, grid lines for structure); Acme-style product cards (bordered cell, photo centered on white, bold UPPERCASE name, small grey subtitle line with color/variant names, a full-width bottom bar with an action on the left and the price right-aligned, in a tight grid of thin divider lines); two fonts only (one bold grotesque/sans for headings, product names, and nav, one clean readable font for body); a big beautiful full-width photo of Yale's campus on the landing page with a short bold headline and one button; tightened hierarchy, subtle tasteful hover/transition motion, and a chat widget that matches the new minimal look. Keep everything working (products, filters, single-item pages, chat, login). Then write output/design.md — short and concrete — covering what I changed and why it should help customers stick around and buy.

**Follow-up prompt:**
> I want to try harder to make the website look like acmecups.nz — thinner lines and square 90° corners on the inventory boxes, no light-blue backgrounds, only two fonts, and a big clear picture of Yale's campus on the landing page. Take as many design cues from that site as you can.

**Why I needed the follow-up:** My first styling pass still had rounded corners, tinted backgrounds, and shadows, so I asked for a stronger, more faithful match to the Acme Cups look.

**Second follow-up prompt:**
> There's too much text — cut it everywhere and only keep words that are really necessary. Make the hero the entire page with the campus photo edge to edge (no border on the sides), just "Campus Customs" and one simple line, and put the navigation on top of the hero instead of a separate bar. Make all the product image backgrounds white. The "shop by collection" boxes should show only the category name.

**Why I needed the second follow-up:** The design was close but still wordy, the hero didn't fill the page, the nav sat in its own bar, and many product photos had black backgrounds, so I asked for a cleaner, more minimal pass.

---

## Problem 11: Site Testing (App Check)

**Prompt:**
> Create output/app_check.html, a simple page I can double-click to open that documents testing of the live site. Give it a heading for each check, the screenshot below it, and one or two sentences saying what the screenshot proves. Put the screenshot image files in output/app_check_images/ and link them with relative paths like app_check_images/inventory.png. Cover three checks: (1) the chat checking an item's inventory level, showing honest stock and price from the database; (2) the dynamic search-result cards appearing on the page after a category question like "what hoodies do you have?"; (3) one of the Problem 9 usability features (the Products filter/sort toolbar). Keep it clean and match the site's style.

---

## Problem 12: Audit Trail, Safety, Finish Harness

**Prompt:**
> Add an append-only audit trail at output/audit_trail.json that records the agent's activity on every chat turn (a timestamp, which tools were called with short args, a short version of each tool's result, and the stop reason) and make sure it's never wiped between runs (new entries append to the existing file). Then add a clear set of safety rules for the agent to prompts/prompt.md (tighten what's already there). Finally, finish output/harness.md so the whole system is documented: the model fields in models.py and why I chose them, the tools and what the agent can do, the safety rules, and a Specs section covering loop limits, result caps, which model is used, and how to run the front end and backend.

---

## Problem 13: Push to GitHub and Submit the URL

**Prompt:**
> This is the final step: push the project to a public GitHub repo so graders can open and clone it. The code lives in a folder named hw4. First write a README.md at the root of hw4 that explains what the project is and how to run it — how to set up the Python backend and the Vite/React frontend, where to put the local data pack (the data/ folder with campus_customs.db and products/), and how to add a Portkey key via backend/.env (copy from .env.example). Make sure .gitignore keeps the real .env, the database, the product images, node_modules, and the venv out of the repo, and that .env.example with placeholder values is included. Confirm the repo matches the expected layout, then help me initialize git, commit, and push to a new public GitHub repo, and give me the repo URL to submit on Canvas.

---
