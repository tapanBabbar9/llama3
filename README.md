# Llama 3

This repository uses Llama 3.1 with Ollama

## Getting Started

Follow these steps to get up and running with the Ollama application and the LLaMA 3.1 model:

### Prerequisites

- Ollama application (v0.3.14 or higher)
- Python 3.x
- Internet connection for downloading the model

### Installation and Setup

1. **Download and Install Ollama**

   First, download the Ollama application from the official website:

   [Ollama Download](https://ollama.com/download)

   Install and run the application on your local machine.

2. **Pull the LLaMA 3.1 Model**

   Once the Ollama app is running, you'll need to pull the LLaMA 3.1 model. Run the following command in your terminal:

   ```bash
   ollama run llama3.1
3. **Run LLaMA 3.1 Model**

   To verify that the model is properly installed and working, list the available models by running the following command:

   ```bash
   ollama list

This will initiate the model, and you'll be able to interact with it via the Ollama interface.


### Notes

Ensure Ollama is running in the background when executing Python scripts.
Replace the prompt with your own custom input to experiment with different AI outputs.

### License

This project is licensed under the MIT License - see the LICENSE file for details.
