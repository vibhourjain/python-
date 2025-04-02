#!/bin/bash

is_bad_file() {
    # Check file exists and is readable
    [ ! -f "$1" ] && echo "ERROR: File $1 not found" >&2 && return 2

    # Verify exactly 3 lines (header, record, footer)
    line_count=$(wc -l < "$1")
    [ "$line_count" -ne 3 ] && return 1

    # Verify header starts with HEADER
    head -1 "$1" | grep -q '^HEADER' || return 1

    # Verify footer is exactly "FOOTER 1"
    [ "$(tail -1 "$1")" != "FOOTER 1" ] && return 1

    # Get the record (second line)
    record=$(sed -n '2p' "$1")

    # Remove all tildes and whitespace - if nothing remains, it's bad
    if [ -z "$(echo "$record" | tr -d '[:space:]~')" ]; then
        return 0  # This is a bad file
    fi

    return 1  # Good file
}

# Test with your examples
test_files=(
    "file1"  # HEADER...~   3456~ ~~...FOOTER 1 (GOOD)
    "file2"  # HEADER...~   ~ a12~~...FOOTER 1 (GOOD)
    "file3"  # HEADER...~   ~ ~~...FOOTER 1 (BAD)
)

for file in "${test_files[@]}"; do
    if is_bad_file "$file"; then
        case $? in
            0) echo "BAD: $file - Empty record with only delimiters" ;;
            1) echo "GOOD: $file - Contains valid data" ;;
            2) echo "ERROR: $file - File not found" ;;
        esac
    else
        echo "GOOD: $file - Contains valid data"
    fi
done