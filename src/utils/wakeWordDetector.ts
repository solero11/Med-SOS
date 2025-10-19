// src/utils/wakeWordDetector.ts
// Wake word detection utility (stub for integration with native or cloud service)

export type WakeWordCallback = (wakeWord: string) => void;

export class WakeWordDetector {
  private callback: WakeWordCallback;
  private listening: boolean = false;
  private supportedWakeWords = ["Hermes", "Hey Hermes"];

  constructor(callback: WakeWordCallback) {
    this.callback = callback;
  }

  // Simulate wake word detection (replace with real implementation)
  public startListening() {
    this.listening = true;
    // In a real app, integrate with a native module or cloud service here
    // For demo, simulate detection after a timeout
    setTimeout(() => {
      if (this.listening) {
        this.callback("Hermes");
      }
    }, 3000); // Simulate detection after 3 seconds
  }

  public stopListening() {
    this.listening = false;
  }

  public isListening() {
    return this.listening;
  }
}

// Usage example (to be integrated in main app logic):
// const detector = new WakeWordDetector((word) => {
//   if (word === "Hermes" || word === "Hey Hermes") {
//     // Activate listening indicator and SOS button logic
//   }
// });
// detector.startListening();
