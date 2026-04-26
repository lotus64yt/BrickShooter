const puppeteer = require("puppeteer");
const path = require("path");

(async () => {
  const username = process.env.MONLYCEE_USERNAME;
  const password = process.env.MONLYCEE_PASSWORD;
  const commitMessage = process.env.COMMIT_MESSAGE;
  const zipPath = path.resolve(process.env.ZIP_PATH);
  const timelineUrl =
    "https://ent.monlycee.net/timelinegenerator#/view/3ff4382a-5f59-4378-af48-c50b1eaa4fb9";

  console.log("Starting Puppeteer...");
  const browser = await puppeteer.launch({
    headless: "new",
    args: ["--no-sandbox", "--disable-setuid-sandbox"],
  });
  const page = await browser.newPage();

  try {
    console.log("Navigating to login page...");
    await page.goto("https://psn.monlycee.net", { waitUntil: "networkidle2" });

    console.log("Logging in...");
    await page.waitForSelector("#username");
    await page.type("#username", username);
    await page.type("#password", password);
    await page.click("#kc-login");

    await page.waitForNavigation({ waitUntil: "networkidle2" });
    console.log("Logged in successfully.");

    console.log(`Navigating to timeline: ${timelineUrl}`);
    await page.goto(timelineUrl, { waitUntil: "networkidle2" });

    console.log('Clicking "Add an event"...');
    const addEventSelector = "button.cell.right-magnet.no-margin.ng-scope";
    await page.waitForSelector(addEventSelector);
    await page.click(addEventSelector);

    console.log("Setting event title...");
    const titleSelector = "input.ten.cell";
    await page.waitForSelector(titleSelector);
    await page.type(titleSelector, commitMessage);

    console.log("Opening file upload modal...");
    const paperclipSelector = "i.v-icon.v-paperclip";
    await page.waitForSelector(paperclipSelector);
    await page.click(paperclipSelector);

    console.log('Waiting for modal and clicking "UPLOAD" tab...');
    await new Promise((resolve) => setTimeout(resolve, 2000));
    const [uploadTab] = await page.$x(
      "//div[contains(text(), 'UPLOAD')] | //button[contains(text(), 'UPLOAD')] | //span[contains(text(), 'UPLOAD')]",
    );
    if (uploadTab) {
      await uploadTab.click();
    } else {
      console.warn(
        "Could not find UPLOAD tab by text, trying to find .upload-input directly...",
      );
    }

    console.log(`Uploading file: ${zipPath}`);
    const fileInputSelector = "input.upload-input";
    await page.waitForSelector(fileInputSelector, { visible: false });
    const inputHandle = await page.$(fileInputSelector);
    await inputHandle.uploadFile(zipPath);

    console.log("Waiting for upload to process...");
    await new Promise((resolve) => setTimeout(resolve, 5000));

    console.log("Publishing/Saving the event...");
    const saveButtonSelector = "button.right-magnet";
    await page.waitForSelector(saveButtonSelector);

    // Find the button that specifically contains 'Enregistrer' or 'Save'
    const buttons = await page.$$(saveButtonSelector);
    let saved = false;
    for (const btn of buttons) {
      const text = await page.evaluate((el) => el.innerText, btn);
      if (
        text.toLowerCase().includes("enregistrer") ||
        text.toLowerCase().includes("save") ||
        text.toLowerCase().includes("publier")
      ) {
        await btn.click();
        saved = true;
        break;
      }
    }

    if (!saved) {
      console.log("Clicking the first available save button...");
      await page.click(saveButtonSelector);
    }

    console.log("Event published successfully!");
    await new Promise((resolve) => setTimeout(resolve, 2000));
  } catch (error) {
    console.error("An error occurred:", error);
    // Take a screenshot for debugging if it fails
    await page.screenshot({ path: "error_screenshot.png" });
    process.exit(1);
  } finally {
    await browser.close();
  }
})();
