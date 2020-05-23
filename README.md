# session_manager_exporter
Python script to export stored sessions from Session Manager plugin into Firefox HTML Bookmark file.

# Usage

```
cd <project_root>
./session_manager_exporter.py <sessions_storage_folder>
```

A file named ``exported_sessions.html`` will be created alongside the script.
Import it from Firefox; Folders will be placed inside the ``Bookmarks Menu`` folder.

# Known issues

1. Only supports sessions containing one window each. Will not parse/save more than one window per session.
1. Does not save tab history.
