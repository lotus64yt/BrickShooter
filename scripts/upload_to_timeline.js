const puppeteer = require("puppeteer");
const path = require("path");
const fs = require("fs");
const archiver = require("archiver");

async function createPyZip(zipPath) {
  return new Promise((resolve, reject) => {
    const output = fs.createWriteStream(zipPath);
    const archive = archiver("zip", { zlib: { level: 9 } });
    output.on("close", () => resolve());
    archive.on("error", (err) => reject(err));
    archive.pipe(output);
    const { globSync } = require("glob");
    const pyFiles = globSync("**/*.py", {
      cwd: __dirname.replace("/scripts", ""),
      ignore: ["node_modules/**", ".venv/**", "venv/**"],
    });
    for (const file of pyFiles) {
      const fullPath = path.join(__dirname.replace("/scripts", ""), file);
      archive.file(fullPath, { name: file });
    }
    archive.finalize();
  });
}

(async () => {
  const username = process.env.MONLYCEE_USERNAME;
  const password = process.env.MONLYCEE_PASSWORD;
  const commitMessage = process.env.COMMIT_MESSAGE;
  const zipPath = path.resolve(process.env.ZIP_PATH);

  await createPyZip(zipPath);

  const timelineUrl =
    "https://ent.monlycee.net/timelinegenerator#/view/3ff4382a-5f59-4378-af48-c50b1eaa4fb9";

  const browser = await puppeteer.launch({
    headless: process.env.HEADLESS !== "false" ? "new" : false,
    args: [
      "--no-sandbox",
      "--disable-setuid-sandbox",
      "--window-size=1920,1080",
    ],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080 });
  await page.setUserAgent(
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
  );

  try {
    console.log("[1] Navigating to timeline...");
    await page.goto(timelineUrl, { waitUntil: "networkidle2", timeout: 60000 });
    console.log("[2] URL:", page.url(), "| Title:", await page.title());

    const hasLogin = await page.$("#username");
    console.log("[3] Login page detected:", !!hasLogin);

    if (hasLogin) {
      await page.type("#username", username);
      await page.type("#password", password);
      await Promise.all([
        page.click("#kc-login"),
        page
          .waitForNavigation({ waitUntil: "networkidle2", timeout: 60000 })
          .catch(() => {}),
      ]);
      console.log("[4] After login. URL:", page.url());
      await new Promise((r) => setTimeout(r, 5000));
    }

    for (let retry = 0; retry < 3; retry++) {
      console.log(`[5] Timeline nav attempt ${retry + 1}`);
      await page.goto(timelineUrl, {
        waitUntil: "networkidle0",
        timeout: 60000,
      });
      await new Promise((r) => setTimeout(r, 8000));

      const url = page.url();
      const title = await page.title();
      const is404 = await page.evaluate(
        () =>
          document.body.innerText.includes("404") ||
          document.body.innerText.includes("Oops") ||
          document.title.includes("Error"),
      );
      console.log(`[5] URL=${url} | Title=${title} | is404=${is404}`);

      if (!is404 && url.includes("timelinegenerator")) {
        console.log("[6] Timeline reached OK.");
        break;
      }
      console.log(`[5] Not on timeline, retrying in 4s...`);
      await new Promise((r) => setTimeout(r, 4000));
    }

    const addEventSelector =
      "button.cell.right-magnet.no-margin.ng-scope, button.cell.right-magnet.no-margin";
    console.log("[7] Waiting for 'Add event' button...");
    await page.waitForSelector(addEventSelector, { timeout: 90000 });
    console.log("[8] Button found, clicking...");
    await page.click(addEventSelector);

    const titleSelector =
      'input[placeholder="Information bubble"], input.ten.cell';
    await page.waitForSelector(titleSelector, { timeout: 30000 });
    await page.type(titleSelector, commitMessage);

    await page.click('div.drawing-zone[role="textbox"]').catch(() => {});
    await new Promise((resolve) => setTimeout(resolve, 2000));

    const paperclipSelector = ".option.attachment, i.v-icon.v-paperclip";
    const folderPencilSelector = "i.edit.pick-file, .v-icon.v-pencil";

    let modalOpened = false;
    if (await page.$(paperclipSelector)) {
      await page.click(paperclipSelector);
      modalOpened = true;
    } else {
      const pencil = await page.$(folderPencilSelector);
      if (pencil) {
        await pencil.click();
        modalOpened = true;
      }
    }

    if (!modalOpened) {
      throw new Error("Could not find upload icon");
    }

    await new Promise((resolve) => setTimeout(resolve, 4000));

    const uploadTab = await page.evaluateHandle(() => {
      const keywords = [
        "UPLOAD",
        "CHARGER",
        "TRANSFÉRER",
        "IMPORTER",
        "TÉLÉCHARGER",
      ];
      const findInDoc = (doc) => {
        const elements = Array.from(
          doc.querySelectorAll("div, button, span, li, a"),
        ).reverse();
        return elements.find((el) => {
          if (el.children.length > 2) return false;
          const text = (el.innerText || el.textContent || "")
            .trim()
            .toUpperCase();
          return keywords.some((kw) => text === kw);
        });
      };
      let found = findInDoc(document);
      if (found) return found;
      for (const iframe of Array.from(document.querySelectorAll("iframe"))) {
        try {
          const innerDoc =
            iframe.contentDocument || iframe.contentWindow.document;
          found = findInDoc(innerDoc);
          if (found) return found;
        } catch (e) {}
      }
      return null;
    });

    if (uploadTab && uploadTab.asElement()) {
      const el = uploadTab.asElement();
      await page.evaluate((e) => {
        e.click();
        if (
          e.parentElement &&
          (e.parentElement.tagName === "LI" ||
            e.parentElement.tagName === "DIV")
        ) {
          e.parentElement.click();
        }
      }, el);
      await new Promise((resolve) => setTimeout(resolve, 5000));
    }

    const fileInputSelector = "input.upload-input, input[type='file']";
    let inputHandle = null;
    const findInputInFrames = async () => {
      for (const frame of page.frames()) {
        try {
          const input = await frame.$(fileInputSelector);
          if (input) return input;
        } catch (e) {}
      }
      return null;
    };

    for (let i = 0; i < 15; i++) {
      inputHandle = await findInputInFrames();
      if (inputHandle) break;
      if (i > 0 && i % 4 === 0 && uploadTab && uploadTab.asElement()) {
        await page.evaluate((e) => e.click(), uploadTab.asElement());
      }
      await new Promise((r) => setTimeout(r, 1000));
    }

    if (inputHandle) {
      await inputHandle.uploadFile(zipPath);
    } else {
      throw new Error("Could not find file input");
    }

    let importBtnClicked = false;
    for (let i = 0; i < 45; i++) {
      const btnHandle = await page.evaluateHandle(() => {
        const keywords = [
          "IMPORT",
          "IMPORTER",
          "AJOUTER",
          "ADD",
          "VALIDER",
          "OK",
        ];
        const findInDoc = (doc) => {
          const buttons = Array.from(
            doc.querySelectorAll(
              "button, .button, div[role='button'], .right-magnet",
            ),
          );
          return buttons.find((b) => {
            const text = (b.innerText || "").trim().toUpperCase();
            const isVisible = b.offsetWidth > 0 && b.offsetHeight > 0;
            return (
              isVisible &&
              keywords.some(
                (kw) => text === kw || (text.length < 15 && text.includes(kw)),
              ) &&
              !b.disabled &&
              !b.classList.contains("disabled")
            );
          });
        };
        let f = findInDoc(document);
        if (f) return f;
        for (const frame of Array.from(document.querySelectorAll("iframe"))) {
          try {
            const inner = frame.contentDocument || frame.contentWindow.document;
            f = findInDoc(inner);
            if (f) return f;
          } catch (e) {}
        }
        return null;
      });

      if (btnHandle && btnHandle.asElement()) {
        const el = btnHandle.asElement();
        await page.evaluate((e) => {
          e.click();
          if (e.parentElement) e.parentElement.click();
        }, el);
        importBtnClicked = true;
        break;
      }
      await new Promise((r) => setTimeout(r, 1000));
    }

    await new Promise((resolve) => setTimeout(resolve, 4000));

    const saveBtnHandle = await page.evaluateHandle(() => {
      const keywords = ["ENREGISTRER", "SAVE", "PUBLIER", "PUBLISH"];
      const buttons = Array.from(
        document.querySelectorAll("button, .button, .right-magnet"),
      );
      return buttons.find((b) => {
        const text = (b.innerText || b.textContent || "").trim().toUpperCase();
        return keywords.some((kw) => text.includes(kw)) && !b.disabled;
      });
    });

    if (saveBtnHandle && saveBtnHandle.asElement()) {
      await saveBtnHandle.asElement().click();
    } else {
      await page.click("button.right-magnet").catch(() => {});
    }

    await new Promise((resolve) => setTimeout(resolve, 3000));
    console.log("[OK] Event published successfully.");
  } catch (error) {
    console.error("[ERROR]", error.message);
    await page.screenshot({ path: "error_screenshot.png" });
    process.exit(1);
  } finally {
    await browser.close();
  }
})();
