// import { runAppleScript } from "@raycast/utils";
import { execSync } from "child_process";
import path from "path";

export default async function Command() {
  try {
    console.log("Starting switch-right command");
    
    // Path to Python interpreter in virtual environment
    const pythonPath = path.join(__dirname, "assets", ".venv", "bin", "python");
    
    // Path to your script
    const scriptPath = path.join(__dirname, "assets", "main.py");
    
    // Execute command
    const result = execSync(`${pythonPath} ${scriptPath} right`, {
      encoding: 'utf-8'
    });
    
    console.log("Script execution result:", result);
  } catch (error) {
    console.error("Error executing script:", error);
    throw error;
  }
}