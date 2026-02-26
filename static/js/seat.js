(function () {
  const checks = document.querySelectorAll(".seat-check");
  const baseFareEl = document.getElementById("baseFare");
  const totalFareEl = document.getElementById("totalFare");
  const selectedSeatsText = document.getElementById("selectedSeatsText");

  if (!checks || !baseFareEl || !totalFareEl || !selectedSeatsText) return;

  const baseFare = parseFloat(baseFareEl.value || "0");

  function updateUI() {
    const selected = Array.from(checks).filter(c => c.checked);
    const seatNames = selected.map(s => s.dataset.seatNumber);

    // Toggle label selected state
    selected.forEach(c => {
      const label = document.querySelector(`label[for="${c.id}"]`);
      if (label) label.classList.add("selected");
    });
    Array.from(checks).filter(c => !c.checked).forEach(c => {
      const label = document.querySelector(`label[for="${c.id}"]`);
      if (label) label.classList.remove("selected");
    });

    selectedSeatsText.textContent = seatNames.length ? seatNames.join(", ") : "None";
    totalFareEl.textContent = (selected.length * baseFare).toFixed(2);
  }

  checks.forEach(c => c.addEventListener("change", updateUI));
  updateUI();
})();