#! /usr/bin/python3

import json
import threading
from subprocess import check_output
from time import sleep
from os import listdir, path, remove

DUMP_FOLDER = "/home/andrew/Downloads"

def is_chrome_open():
  for window in check_output(['wmctrl', '-l']).decode('utf-8').splitlines():
    if 'Google Chrome' in window:
      return True
  return False

def is_dump_file(file):
  return file.startswith("window_tab_dump_") and file.endswith(".json")

def clear_window_tab_dumps():
  for file in listdir(DUMP_FOLDER):
    if is_dump_file(file):
      remove(path.join(DUMP_FOLDER, file))

def parse_latest_window_tab_dump():
  max_file = None
  max_timestamp = 0
  for file in listdir(DUMP_FOLDER):
    if is_dump_file(file):
      timestamp = int(file.replace("window_tab_dump_", "").replace(".json", ""))
      if timestamp > max_timestamp:
        max_timestamp = timestamp
        max_file = file

  if max_timestamp == 0:
    return None

  with open(path.join(DUMP_FOLDER, max_file), "r") as reader:
    return json.loads(reader.read())

# Returns a dict of (window handle => list of tabs in the shape {url, title, ...})
def get_chrome_windows():
  # Read window manager
  chrome_windows = {}
  titles = {} # Map title -> handle
  for window in check_output(['wmctrl', '-l']).decode('utf-8').splitlines():
    if not 'Google Chrome' in window:
      continue

    handle, desktop, username = window.split()[:3]
    chrome_windows[handle] = None

    title = window[window.index(username)+len(username)+1 : -len(" - Google Chrome")]
    titles[title] = handle

  print("titles")
  print(titles)

  # Use titles to cross reference with the dump
  dump = parse_latest_window_tab_dump()
  for window in dump.values():
    title = [tab['title'] for tab in window['tabs'] if tab['selected']][0]
    handle = titles[title]
    chrome_windows[handle] = window['tabs']

  return chrome_windows

def move_to_desktop(handle, desktop):
  return check_output(['wmctrl', '-i', '-r', handle, '-t', str(desktop)])

if is_chrome_open():
  print("Close Chrome first")
  sleep(3)
  exit()

# Launch Chrome and wait for window tab dump
clear_window_tab_dumps()
threading.Thread(target=lambda: check_output(["/usr/bin/google-chrome"])).start()
sleep(2)
while parse_latest_window_tab_dump() is None:
  sleep(2)

# Restore windows
#
# We'll look for an "anchor tab" in each window.
# An anchor tab is a tab with a known URL/name that determines which desktop a window should go on.
# If a window has no anchor tab, it will go to the FALLBACK desktop.
FALLBACK = 0
ANCHORS = {
  'spotify.com': 1,
  'canvas.uw.edu': 2,
  'Idea #4': 3,
}

for handle, tabs in get_chrome_windows().items():
  desktop = FALLBACK
  if tabs is None:
    print("no tabs for handle = ", handle)
  for tab in tabs:
    for anchor, anchor_desktop in ANCHORS.items():
      if anchor in tab['url'] or anchor in tab['title']:
        desktop = anchor_desktop
        # print(f"moving {handle} to {desktop}")
        # if anchor in tab['url']:
        #   print(f"  - because url {anchor} in {tab['url']}")
        # if anchor in tab['title']:
        #   print(f"  - because title {anchor} in {tab['title']}")
        # TODO: break twice?
  move_to_desktop(handle, desktop)

clear_window_tab_dumps()
