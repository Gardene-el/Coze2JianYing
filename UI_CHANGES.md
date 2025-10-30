## UI Changes - New "生成元信息" Button

### Button Layout (Before and After)

**Before:**
```
[生成草稿] [清空] [隐藏日志]
```

**After:**
```
[生成草稿] [生成元信息] [清空] [隐藏日志]
```

### New Button Details

- **Button Text**: "生成元信息"
- **Position**: Between "生成草稿" and "清空" buttons
- **Function**: Triggers independent generation of `root_meta_info.json`

### User Flow

1. User clicks "生成元信息" button
2. System validates the selected folder (or auto-detects if not selected)
3. Confirmation dialog appears: "将在以下文件夹生成 root_meta_info.json: {folder}\n\n是否继续？"
4. If user confirms:
   - System scans the folder for draft files
   - Generates `root_meta_info.json` in the folder
   - Shows success message with file path
5. If user cancels or there's an error:
   - Shows appropriate error message

### Key Features

- **Independent Operation**: Can be triggered without generating drafts
- **Folder Validation**: Validates folder exists and is accessible
- **User Confirmation**: Asks for confirmation before generating
- **Progress Indication**: Disables button and shows status during generation
- **Error Handling**: Shows detailed error messages if generation fails
- **Log Integration**: Shows generation progress in the log panel

### Technical Implementation

**File**: `src/gui/main_window.py`
- Added `generate_meta_btn` button widget
- Implemented `_generate_meta_info()` method
- Integrated with existing folder selection system

**File**: `src/utils/draft_generator.py`
- Converted `_generate_root_meta_info()` to public `generate_root_meta_info(folder_path=None)`
- Removed automatic calls from `generate()` and `generate_from_file()` methods
- Added optional `folder_path` parameter for flexibility
