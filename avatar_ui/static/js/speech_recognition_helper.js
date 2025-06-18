// static/js/speech_recognition_helper.js

let recognition = null;
let recognitionPromiseResolve = null;
let recognitionPromiseReject = null;

// Initialize SpeechRecognition if available
if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.continuous = false; // Only get one result per recognition session
    recognition.lang = 'en-US'; // Set language
    recognition.interimResults = false; // We only want final results
    recognition.maxAlternatives = 1; // Only get the most likely alternative

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        console.log('JS: Speech recognition result:', transcript);
        if (recognitionPromiseResolve) {
            recognitionPromiseResolve(transcript);
            recognitionPromiseResolve = null;
            recognitionPromiseReject = null;
        }
    };

    recognition.onerror = (event) => {
        console.error('JS: Speech recognition error:', event.error);
        if (recognitionPromiseReject) {
            recognitionPromiseReject(event.error);
            recognitionPromiseResolve = null;
            recognitionPromiseReject = null;
        }
    };

    recognition.onend = () => {
        console.log('JS: Speech recognition service ended.');
        // If the promise hasn't been resolved/rejected yet (e.g., no speech detected),
        // we might want to resolve with an empty string or reject.
        if (recognitionPromiseResolve) {
            recognitionPromiseResolve(""); // Resolve with empty string if nothing was said
            recognitionPromiseResolve = null;
            recognitionPromiseReject = null;
        }
    };

    recognition.onstart = () => {
        console.log('JS: Speech recognition service started.');
    };

} else {
    console.warn('JS: Web Speech API not supported in this browser.');
}

/**
 * Starts the speech recognition service.
 * Returns a Promise that resolves with the transcribed text or rejects with an error.
 * This function is exposed globally for PyScript to call.
 */
window.startSpeechRecognition = function() {
    return new Promise((resolve, reject) => {
        if (!recognition) {
            console.error('JS: SpeechRecognition not initialized or not supported.');
            return reject('SpeechRecognition not available.');
        }

        // Ensure no previous promise is pending
        if (recognitionPromiseResolve) {
            recognitionPromiseReject('Recognition already in progress.');
            console.warn('JS: Previous speech recognition attempt cancelled due to new request.');
        }
        
        recognitionPromiseResolve = resolve;
        recognitionPromiseReject = reject;

        try {
            recognition.start();
            console.log('JS: Recognition started.');
        } catch (e) {
            console.error('JS: Error starting recognition:', e);
            reject(e.message || 'Error starting recognition.');
        }
    });
};

/**
 * Stops the speech recognition service.
 * This function is exposed globally for PyScript to call.
 */
window.stopSpeechRecognition = function() {
    if (recognition && recognitionPromiseResolve) {
        recognition.stop();
        console.log('JS: Recognition stopped.');
    }
};