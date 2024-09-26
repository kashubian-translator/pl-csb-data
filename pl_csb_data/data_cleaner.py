import os
import re


def remove_matching_phrases(polish_file_path, kashubian_file_path, search_phrases, search_in='both'):
    if search_in not in ['polish', 'kashubian', 'both']:
        raise ValueError("search_in parameter must be 'polish', 'kashubian', or 'both'")

    temp_polish_path = polish_file_path + '.tmp'
    temp_kashubian_path = kashubian_file_path + '.tmp'

    with open(polish_file_path, 'r', encoding='utf-8') as polish_file, \
            open(kashubian_file_path, 'r', encoding='utf-8') as kashubian_file, \
            open(temp_polish_path, 'w', encoding='utf-8') as temp_polish_file, \
            open(temp_kashubian_path, 'w', encoding='utf-8') as temp_kashubian_file:

        for polish_line, kashubian_line in zip(polish_file, kashubian_file):
            modified_polish_line = polish_line.strip()
            modified_kashubian_line = kashubian_line.strip()

            if search_in in ['polish', 'both']:
                for phrase in search_phrases:
                    modified_polish_line = modified_polish_line.replace(phrase, '').strip()

            if search_in in ['kashubian', 'both']:
                for phrase in search_phrases:
                    modified_kashubian_line = modified_kashubian_line.replace(phrase, '').strip()

            if not modified_polish_line or not modified_kashubian_line or len(modified_polish_line) < 2 or len(modified_kashubian_line) < 2:
                continue  # We don't want empty nor one-letter lines

            modified_kashubian_line = re.sub(r'\s+', ' ', modified_kashubian_line)
            modified_polish_line = re.sub(r'\s+', ' ', modified_polish_line)

            temp_polish_file.write(modified_polish_line + '\n')
            temp_kashubian_file.write(modified_kashubian_line + '\n')

    os.replace(temp_polish_path, polish_file_path)
    os.replace(temp_kashubian_path, kashubian_file_path)


def remove_duplicated_phrases(polish_file_path, kashubian_file_path):
    temp_polish_path = polish_file_path + '.tmp'
    temp_kashubian_path = kashubian_file_path + '.tmp'

    seen_phrases = set()
    polish_content = []
    kashubian_content = []

    with open(polish_file_path, 'r', encoding='utf-8') as polish_file, \
            open(kashubian_file_path, 'r', encoding='utf-8') as kashubian_file:

        for polish_line, kashubian_line in zip(polish_file, kashubian_file):
            polish_line = polish_line.strip()
            kashubian_line = kashubian_line.strip()

            line_pair = (polish_line, kashubian_line)

            if line_pair not in seen_phrases:
                seen_phrases.add(line_pair)
                polish_content.append(polish_line + '\n')
                kashubian_content.append(kashubian_line + '\n')

    with open(temp_polish_path, 'w', encoding='utf-8') as temp_polish_file, \
            open(temp_kashubian_path, 'w', encoding='utf-8') as temp_kashubian_file:
        temp_polish_file.writelines(polish_content)
        temp_kashubian_file.writelines(kashubian_content)

    os.replace(temp_polish_path, polish_file_path)
    os.replace(temp_kashubian_path, kashubian_file_path)


def clean_data():
    phrases_to_remove = [
        'GNOME', 'File', '_', 'Launchpad Contributions: Mark Kwidzińsczi https://launchpad.net/~kaszeba', 'view-type',
        'view-size', 'item-set', 'undo-type', 'thumbnail-size', 'dash-preset', 'ink-blob-type', 'GIMP', '%s', '%d', ':',
        'cap-style', 'join-style', 'fill-type', 'align-reference-type', 'convert-palette-type', '...', '""', '^', '\'',
        'convert-dither-type', 'cursor-format', 'handedness', 'window-hint', 'help-browser-type', 'Date Modified', '%',
        'zoom-quality', 'space-bar-action', 'canvas-padding-mode', 'cursor-mode', 'layer-mode-effects', '7zip', 'ACE',
        'curve-type', 'color-frame-mode', 'histogram-channel', 'message-severity', 'windows-action', '(', ')', 'command',
        'view-padding-color', 'view-zoom-action', 'view-action', 'vectors-action', 'tools-action', 'text-editor-action',
        'tool-presets-action', 'text-tool-action', 'tool-options-action', 'split into volumes of 10.0 MB', '&', '[', ']',
        'templates-action', 'select-action', 'plug-in-action', 'patterns-action', 'palettes-action', '1', '2', '3', '4',
        '5', '6', '7', '8', '9', '0', '+', 'ColorSmart', 'QSQLiteResult', 'QMYSQLResult', 'QRegExp', 'QIODevice', '/',
        'palette-editor-action', 'layers-action', 'image-convert-action', 'gradients-action', 'gradient-editor-coloring',
        'gradient-editor-action', 'gradient-editor-color-type', 'file-action', 'edit-action', 'transform-type', 'action',
        'dynamics-action', 'image-action', 'drawable-action', 'undo-desc', 'documents-action', 'sample-points-action',
        'dockable-action', 'tab-style', 'preview-size', 'dock-action', 'dialogs-action', 'cursor-info-action', 'inmenu',
        'context-action', 'config-action', 'colormap-action', 'channels-action', 'buffers-action', 'The quality of music',
        'brushes-action', 'dynamics-output-type', 'select-criterion', 'vector-mode', 'tool-preset-editor-action', 'Number',
        'quick-mask-action', 'images-action', 'help-action', 'gradient-editor-blending', 'phrase', 'fonts-action', 'entries'
        'error-console-action', 'dynamics-editor-action', 'pre', 'brush-editor-action', 'fill-style', 'stroke-method', '×',
        'QPrintPreviewDialog', 'QShortcut', '*', 'NativeSocketEngine', 'context menu item', 'QSystemSemaphore', 'column'
        'Media controller element', 'PulseAudio', 'QIBaseResult', 'QIBaseDriver', 'QUnicodeControlCharacterMenu', 'window',
        'QFontDatabase', 'MB', 'QNetworkAccessBackend', 'QNetworkAccessDebugPipeBackend', 'QNetworkReply', '@', 'title',
        'QSocksSocketEngine', 'Name', 'Description', 'Comment', 'item Undo action item', 'XLIFF mark type', 'info tooltip',
        'dpi x dpi', 'x dpi', 'x DPI', 'Media', 'time', 'description', 'QDialogButtonBox', 'View', 'item', 'inlistbox',
        'ShortPossessive', 'month', 'National', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'rich',
        'Sunday', 'LongPossessive', 'Short', 'weekday', 'Day', 'Long', 'Ethiopian', '‘', '’', '”', '“', 'filename', 'plain',
        "\" \"", 'image'
    ]
    polish_file = 'data/dataset.pl.txt'
    kashubian_file = 'data/dataset.csb.txt'
    remove_matching_phrases(polish_file, kashubian_file, phrases_to_remove, 'both')
    remove_duplicated_phrases(polish_file, kashubian_file)


clean_data()
