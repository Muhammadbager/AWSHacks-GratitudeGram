const form = document.getElementById("gratitude-form");
const submitBtn = document.getElementById("submit-btn");
const resultSection = document.getElementById("result");
const errorSection = document.getElementById("error");
const errorText = document.getElementById("error-text");
const letterEl = document.getElementById("letter-text");
const cardImg = document.getElementById("card-image");
const imageLoading = document.getElementById("image-loading");
const regenerateBtn = document.getElementById("regenerate-btn");
const printBtn = document.getElementById("print-btn");

function readForm() {
  const data = new FormData(form);
  return Object.fromEntries(data.entries());
}

function showError(message) {
  errorText.textContent = message;
  errorSection.classList.remove("hidden");
}

function hideError() {
  errorSection.classList.add("hidden");
}

async function postJSON(url, payload) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(body.error || `HTTP ${res.status}`);
  return body;
}

async function generate() {
  hideError();
  const payload = readForm();

  submitBtn.disabled = true;
  submitBtn.textContent = "Writing your letter…";
  resultSection.classList.remove("hidden");
  letterEl.textContent = "";
  cardImg.removeAttribute("src");
  imageLoading.classList.remove("hidden");

  // Fire both Bedrock calls in parallel so the demo feels fast.
  const letterPromise = postJSON("/api/letter", payload)
    .then((res) => {
      letterEl.textContent = res.letter;
    })
    .catch((err) => {
      showError(`Letter generation failed: ${err.message}`);
    });

  const cardPromise = postJSON("/api/card", payload)
    .then((res) => {
      cardImg.src = res.image_url;
      imageLoading.classList.add("hidden");
    })
    .catch((err) => {
      imageLoading.classList.add("hidden");
      showError(`Card image failed: ${err.message}`);
    });

  await Promise.allSettled([letterPromise, cardPromise]);

  submitBtn.disabled = false;
  submitBtn.textContent = "Generate my card";
  resultSection.scrollIntoView({ behavior: "smooth", block: "start" });
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  generate();
});

regenerateBtn.addEventListener("click", generate);
printBtn.addEventListener("click", () => window.print());
