/**
 * Smart Learn - AI-Powered Learning Assistant
 * Frontend Application Script
 */

document.addEventListener("DOMContentLoaded", () => {
  // Initialize Backend Health Check
  checkBackendHealth();
});

/**
 * Checks backend health endpoint and updates UI status badge.
 */
async function checkBackendHealth() {
  const statusBadge = document.getElementById("backendStatus");
  const statusText = document.getElementById("statusText");

  if (!statusBadge || !statusText) return;

  // Determine health check URL (supports direct file access or server access)
  const healthUrl = window.location.origin.startsWith("http")
    ? `${window.location.origin}/api/health`
    : "http://127.0.0.1:8000/api/health";

  try {
    const response = await fetch(healthUrl, { method: "GET" });

    if (response.ok) {
      const data = await response.json();
      if (data && data.status === "success") {
        updateStatusBadge(statusBadge, statusText, true, "Backend: Connected");
        console.log("Smart Learn API Health Status:", data);
        return;
      }
    }

    updateStatusBadge(statusBadge, statusText, false, "Backend: Not Connected");
  } catch (error) {
    console.warn("Could not connect to Smart Learn backend:", error.message);
    updateStatusBadge(statusBadge, statusText, false, "Backend: Not Connected");
  }
}

/**
 * Updates UI badge state and text
 */
function updateStatusBadge(badgeElement, textElement, isConnected, text) {
  badgeElement.className = "status-badge " + (isConnected ? "connected" : "disconnected");
  textElement.textContent = text;
}
