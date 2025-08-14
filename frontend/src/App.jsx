import { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [ports, setPorts] = useState([]);
  const [selectedPort, setSelectedPort] = useState('');
  const [presets, setPresets] = useState([]);
  const [selectedPreset, setSelectedPreset] = useState('Default');
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState('');
  const [status, setStatus] = useState('Ready');
  const [gcode, setGcode] = useState('');

  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        setStatus('Fetching initial data...');
        // Fetch serial ports
        const portsResponse = await fetch('/list-serial-ports');
        const portsData = await portsResponse.json();
        setPorts(portsData.ports);
        if (portsData.ports.length > 0) {
          setSelectedPort(portsData.ports[0]);
        }

        // Fetch presets
        const presetsResponse = await fetch('/list-presets');
        const presetsData = await presetsResponse.json();
        setPresets(presetsData.presets);
        if (presetsData.presets.length > 0) {
          setSelectedPreset(presetsData.presets[0]);
        }

        setStatus('Ready');
      } catch (error) {
        console.error('Error fetching initial data:', error);
        setStatus('Error fetching initial data.');
      }
    };
    fetchInitialData();
  }, []);

  const handleFileChange = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setSelectedFile(file);

    // Get image preview
    try {
      setStatus('Processing image for preview...');
      const formData = new FormData();
      formData.append('file', file);
      const response = await fetch('/process-image/', {
        method: 'POST',
        body: formData,
      });
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      setPreviewUrl(url);
      setStatus('Ready');
    } catch (error) {
      console.error('Error processing image:', error);
      setStatus('Error processing image.');
    }
  };

  const handleEngrave = async () => {
    if (!selectedFile || !selectedPort) {
      setStatus('Please select a file and a serial port.');
      return;
    }

    try {
      // 1. Generate G-code
      setStatus('Generating G-code...');
      const formData = new FormData();
      formData.append('file', selectedFile);
      const gcodeResponse = await fetch(`/generate-gcode/?preset=${selectedPreset}`, {
        method: 'POST',
        body: formData,
      });
      const gcodeText = await gcodeResponse.text();
      setGcode(gcodeText);

      // 2. Send G-code to engraver
      setStatus('Sending G-code to engraver...');
      const sendResponse = await fetch('/send-gcode', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          port: selectedPort,
          gcode: gcodeText,
        }),
      });

      if (sendResponse.ok) {
        setStatus('Engraving started successfully!');
      } else {
        const errorData = await sendResponse.json();
        setStatus(`Error: ${errorData.detail}`);
      }
    } catch (error) {
      console.error('Error during engraving process:', error);
      setStatus('Error during engraving process.');
    }
  };

  return (
    <div className="App">
      <h1>Laser Engraver Control</h1>
      <div className="card">
        <h2>1. Select Device and Material</h2>
        <div className="form-group">
          <label>Serial Port:</label>
          <select
            value={selectedPort}
            onChange={(e) => setSelectedPort(e.target.value)}
            disabled={ports.length === 0}
          >
            {ports.length > 0 ? (
              ports.map((port) => (
                <option key={port} value={port}>
                  {port}
                </option>
              ))
            ) : (
              <option>No ports found</option>
            )}
          </select>
        </div>
        <div className="form-group">
          <label>Material Preset:</label>
          <select
            value={selectedPreset}
            onChange={(e) => setSelectedPreset(e.target.value)}
            disabled={presets.length === 0}
          >
            {presets.map((preset) => (
              <option key={preset} value={preset}>
                {preset}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="card">
        <h2>2. Upload Image</h2>
        <input type="file" accept="image/*" onChange={handleFileChange} />
        {previewUrl && (
          <div>
            <h3>Preview</h3>
            <img src={previewUrl} alt="Preview" style={{ maxWidth: '300px', border: '1px solid #ccc' }} />
          </div>
        )}
      </div>

      <div className="card">
        <h2>3. Start Engraving</h2>
        <button onClick={handleEngrave} disabled={!selectedFile || !selectedPort}>
          Start Engraving
        </button>
      </div>

      <div className="card">
        <h2>Status</h2>
        <p>{status}</p>
      </div>

      <div className="card">
        <h2>Generated G-code</h2>
        <textarea readOnly value={gcode} style={{ width: '100%', height: '200px' }} />
      </div>
    </div>
  );
}

export default App;
