// The devtools page itself is never rendered — its only job is to register the
// panel that hosts the Argos UI inside the DevTools window.
const PANEL_TITLE = "Argos";
const PANEL_ICON = "";
const PANEL_PAGE = "devtools-panel.html";

chrome.devtools.panels.create(PANEL_TITLE, PANEL_ICON, PANEL_PAGE);
