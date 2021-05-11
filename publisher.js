/*
  Example window:
  {
    alwaysOnTop: false
    focused: false
    height: 994
    id: 187
    incognito: false
    left: 3840
    state: "maximized"
    top: 27
    type: "normal"
    width: 1920
  }

  Example tab:
  {"active":false,"audible":false,"autoDiscardable":true,"discarded":true,"favIconUrl":"data:image/png;base64,iV...","height":0,"highlighted":false,"id":806,"incognito":false,"index":0,"mutedInfo":{"muted":false},"pinned":false,"selected":false,"status":"complete","title":"PlantChess - Google Drive","url":"chrome-extension://klbibkeccnjlkjkiokjodocebajanakg/suspended.html#ttl=PlantChess%20-%20Google%20Drive&pos=0&uri=https://drive.google.com/drive/u/0/folders/19zrEm2G_jAGN-Jgj6tRTV_uOfVW4wMMO","width":0,"windowId":187}
*/

function dump(json) {
  for(const id of [...Object.keys(json)]) {
    for(const tab of [...Object.values(json[id].tabs)]) {
      if(tab.title === "...") { // Tab titles aren't instantly available so retry if they aren't
        setTimeout(init, 500);
        return;
      }
    }
  }

  const blob = new Blob([JSON.stringify(json)], {type: "text/json"});
  const url = URL.createObjectURL(blob);
  chrome.downloads.download({
    url,
    filename: `window_tab_dump_${Date.now()}.json`
  }, () => {
    chrome.downloads.setShelfEnabled(false); // Hide download bar
  });
}

function init() {
  chrome.windows.getAll(windows => {
    const windowsWithTabs = {};
    let numTabsDone = 0;
    for(const window of windows) {
      windowsWithTabs[window.id] = window;
      chrome.tabs.getAllInWindow(window.id, tabs => {
        windowsWithTabs[window.id].tabs = tabs;
        numTabsDone++;
        if(numTabsDone === windows.length) {
          dump(windowsWithTabs);
        }
      });
    }
  });
}

init();
