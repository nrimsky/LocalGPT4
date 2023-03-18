import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import "./App.css";
import { RotatingTriangles } from "react-loader-spinner";

function App() {
  const [audioSrc, setAudioSrc] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const audioRef = useRef(null);

  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.playbackRate = 1.4; // Set the playback rate to 1.4x
    }
  }, [audioSrc]);

  const handleClick = async () => {
    if (loading) {
      return;
    }
    setAudioSrc("");
    setLoading(true);
    setErrorMessage("");
    try {
      // Get user's location
      const location = await new Promise((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(resolve, reject);
      });

      // Send location data to the backend
      const response = await axios.post("/api/generate-podcast", {
        location: {
          latitude: location.coords.latitude,
          longitude: location.coords.longitude,
        },
      });

      // Update the audio source and play the audio
      setLoading(false);
      setAudioSrc(`data:audio/mp3;base64,${response.data.audio}`);
    } catch (error) {
      console.error("Error fetching and playing the podcast:", error);
      setErrorMessage(error.message);
      setLoading(false);
      setAudioSrc("");
    }
  };

  return (
    <div className="App">
      <div className="App-body">
        <h1>Your local talking AI</h1>
        {loading && (
          <RotatingTriangles
            visible={true}
            height="80"
            width="80"
            ariaLabel="rotating-triangels-loading"
            wrapperStyle={{}}
            wrapperClass="rotating-triangels-wrapper"
          />
        )}
        <button onClick={handleClick} disabled={loading}>
          {loading ? "Loading..." : "Generate"}
        </button>
        {audioSrc && <audio src={audioSrc} controls ref={audioRef} />}
        <p>
          This app uses your current location to generate a short unique podcast
          about your surrounding area. Enjoy!
        </p>
        {errorMessage && <p className="error-message">Error: {errorMessage}</p>}
      </div>
    </div>
  );
}

export default App;
