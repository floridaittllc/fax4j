#!/bin/sh
set -e

# Check for JDK presence
if command -v javac >/dev/null 2>&1; then
  echo "JDK found: $(javac -version 2>&1)"
elif [ -n "$JAVA_HOME" ] && [ -x "$JAVA_HOME/bin/javac" ]; then
  echo "Using JDK from JAVA_HOME: $JAVA_HOME"
else
  echo "Error: JDK not found. Please install a JDK (e.g., 'sudo apt install openjdk-17-jdk') and rerun this script." >&2
  exit 1
fi

# Run the build
./build.sh
