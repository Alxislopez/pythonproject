import React, { useState } from 'react';
import axios from 'axios';
import { 
  Container, 
  Typography, 
  TextField, 
  Button, 
  Paper, 
  Box, 
  FormControl, 
  InputLabel, 
  Select, 
  MenuItem,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  Divider,
  FormControlLabel,
  Switch,
  Slider
} from '@mui/material';
import './App.css';

const API_URL = 'http://localhost:8000';

function App() {
  const [text, setText] = useState('');
  const [file, setFile] = useState(null);
  const [featureType, setFeatureType] = useState('numbers');
  const [ngramSize, setNgramSize] = useState(2);
  const [base, setBase] = useState(10);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [summarize, setSummarize] = useState(false);
  const [summaryRatio, setSummaryRatio] = useState(0.2);
  const [rawContent, setRawContent] = useState('');
  const [contentType, setContentType] = useState('');
  const [successCopy, setSuccessCopy] = useState(false);

  const handleTextSubmit = async () => {
    if (!text.trim()) {
      setError('Please enter some text to process');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post(`${API_URL}/api/process`, {
        text,
        feature_type: featureType,
        ngram_size: ngramSize,
        base,
        summarize,
        summary_ratio: summaryRatio
      });
      
      setResults(response.data);
    } catch (err) {
      setError(`Error processing text: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleFileSubmit = async () => {
    if (!file) {
      setError('Please select a file to upload');
      return;
    }

    setLoading(true);
    setError('');

    const formData = new FormData();
    formData.append('file', file);
    formData.append('feature_type', featureType);
    formData.append('ngram_size', ngramSize);
    formData.append('base', base);
    formData.append('summarize', summarize);
    formData.append('summary_ratio', summaryRatio);
    
    try {
      const response = await axios.post(`${API_URL}/api/upload-file`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      setResults(response.data);
    } catch (err) {
      setError(`Error processing file: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleViewText = async () => {
    if (!text.trim() && !results) {
      setError('Please process some text first');
      return;
    }
    
    setLoading(true);
    setError('');
    
    const url = `${API_URL}/api/raw-text`;
    console.log('Attempting to fetch text from URL:', url);
    
    try {
      const response = await axios.post(url, {
        text: text || "Sample text",
        feature_type: featureType,
        ngram_size: ngramSize,
        base,
        summarize,
        summary_ratio: summaryRatio
      });
      
      console.log('Response received:', response);
      setRawContent(response.data.content);
      setContentType('text');
    } catch (err) {
      console.error('Error getting text content:', err);
      setError(`Error retrieving text content: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleViewCSV = async () => {
    if (!text.trim() && !results) {
      setError('Please process some text before viewing CSV');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const url = `${API_URL}/api/raw-csv`;
      console.log('Attempting to fetch CSV from URL:', url);
      
      const response = await axios.post(url, {
        text: text || "Sample text",
        feature_type: featureType,
        ngram_size: ngramSize,
        base,
        summarize,
        summary_ratio: summaryRatio
      });
      
      console.log('Response received:', response);
      setRawContent(response.data.content);
      setContentType('csv');
    } catch (err) {
      console.error('Error getting CSV content:', err);
      setError(`Error retrieving CSV content: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleCopyContent = () => {
    navigator.clipboard.writeText(rawContent)
      .then(() => {
        setSuccessCopy(true);
        setTimeout(() => setSuccessCopy(false), 2000);
        alert('Content copied to clipboard!');
      })
      .catch((err) => {
        console.error('Failed to copy content:', err);
        setError('Failed to copy content to clipboard');
      });
  };

  const testApiConnection = async () => {
    try {
      setLoading(true);
      console.log('Testing API connection at:', `${API_URL}/api/text-test`);
      
      const response = await axios.get(`${API_URL}/api/text-test`);
      alert(`API test successful: ${JSON.stringify(response.data)}`);
      
      setRawContent(response.data.content);
      setContentType('text');
    } catch (err) {
      console.error('API test error:', err);
      setError(`API test failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ my: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom align="center" color="primary">
          ML Data Convertor
        </Typography>
        <Typography variant="subtitle1" align="center" color="text.secondary" paragraph>
          Process text and extract features using advanced machine learning techniques
        </Typography>

        <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
          <Typography variant="h5" gutterBottom>
            Configure Processing
          </Typography>
          <Box sx={{ mt: 2 }}>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel id="feature-type-label">Feature Type</InputLabel>
              <Select
                labelId="feature-type-label"
                value={featureType}
                label="Feature Type"
                onChange={(e) => setFeatureType(e.target.value)}
              >
                <MenuItem value="words">Words</MenuItem>
                <MenuItem value="sentences">Sentences</MenuItem>
                <MenuItem value="ngrams">N-grams</MenuItem>
                <MenuItem value="numbers">Numbers</MenuItem>
              </Select>
            </FormControl>
            
            {featureType === 'ngrams' && (
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel id="ngram-size-label">N-gram Size</InputLabel>
                <Select
                  labelId="ngram-size-label"
                  value={ngramSize}
                  label="N-gram Size"
                  onChange={(e) => setNgramSize(e.target.value)}
                >
                  {[2, 3, 4, 5].map(size => (
                    <MenuItem key={size} value={size}>{size}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            )}
            
            {featureType === 'numbers' && (
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel id="base-label">Number Base</InputLabel>
                <Select
                  labelId="base-label"
                  value={base}
                  label="Number Base"
                  onChange={(e) => setBase(e.target.value)}
                >
                  {[2, 8, 10, 16].map(base => (
                    <MenuItem key={base} value={base}>{base}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            )}
            
            <FormControlLabel
              control={
                <Switch
                  checked={summarize}
                  onChange={(e) => setSummarize(e.target.checked)}
                  color="primary"
                />
              }
              label="Generate Text Summary"
            />
            
            {summarize && (
              <Box sx={{ mt: 2, width: '100%', maxWidth: 300 }}>
                <Typography gutterBottom>
                  Summary Length: {Math.round(summaryRatio * 100)}% of original
                </Typography>
                <Slider
                  value={summaryRatio}
                  onChange={(e, newValue) => setSummaryRatio(newValue)}
                  step={0.05}
                  min={0.1}
                  max={0.5}
                  valueLabelDisplay="auto"
                  valueLabelFormat={(value) => `${Math.round(value * 100)}%`}
                />
              </Box>
            )}
          </Box>
        </Paper>

        <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
          <Typography variant="h5" gutterBottom>
            Enter Text
          </Typography>
          <TextField
            label="Text to Process"
            multiline
            rows={6}
            fullWidth
            variant="outlined"
            value={text}
            onChange={(e) => setText(e.target.value)}
            sx={{ mb: 2 }}
          />
          <Button 
            variant="contained" 
            color="primary" 
            onClick={handleTextSubmit}
            disabled={loading}
          >
            Process Text
          </Button>
        </Paper>

        <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
          <Typography variant="h5" gutterBottom>
            Upload File
          </Typography>
          <Box sx={{ mb: 2 }}>
            <input
              accept=".txt,.csv,.json,.pdf,.xlsx,.xls"
              id="file-upload"
              type="file"
              onChange={handleFileChange}
              style={{ display: 'none' }}
            />
            <label htmlFor="file-upload">
              <Button variant="outlined" component="span">
                Select File
              </Button>
            </label>
            {file && (
              <Typography variant="body2" sx={{ mt: 1 }}>
                Selected: {file.name}
              </Typography>
            )}
            <Typography variant="caption" display="block" sx={{ mt: 1, color: 'text.secondary' }}>
              Supported formats: TXT, CSV, JSON, PDF, Excel (XLSX/XLS)
            </Typography>
          </Box>
          <Button 
            variant="contained"
            color="secondary" 
            onClick={handleFileSubmit}
            disabled={loading || !file}
          >
            Process File
          </Button>
        </Paper>

        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
            <CircularProgress />
          </Box>
        )}

        {error && (
          <Paper elevation={3} sx={{ p: 3, mb: 4, bgcolor: '#ffebee' }}>
            <Typography color="error">{error}</Typography>
          </Paper>
        )}

        {results && (
          <Paper elevation={3} sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h5">Results</Typography>
              <Box>
                <Button 
                  variant="contained" 
                  color="primary"
                  onClick={handleViewCSV}
                  disabled={loading}
                  sx={{ mr: 1 }}
                >
                  View as CSV
                </Button>
                <Button 
                  variant="contained" 
                  color="secondary"
                  onClick={handleViewText}
                  disabled={loading}
                  sx={{ mr: 1 }}
                >
                  View as Text
                </Button>
              </Box>
            </Box>
            
            <Box sx={{ mb: 2 }}>
              <Typography><strong>Processing Time:</strong> {results.processing_time.toFixed(4)} seconds</Typography>
              <Typography><strong>Features Processed:</strong> {results.feature_count}</Typography>
              <Typography><strong>Sorting Method:</strong> Optimized Radix Sort (Base: {base})</Typography>
            </Box>
            
            {results.summary && (
              <>
                <Divider sx={{ my: 2 }} />
                <Typography variant="h5" gutterBottom color="primary">
                  Text Summary:
                </Typography>
                <Paper 
                  variant="outlined" 
                  sx={{ p: 3, mb: 3, bgcolor: '#f8f8f8', borderColor: 'primary.light' }}
                >
                  <Typography variant="body1">{results.summary}</Typography>
                </Paper>
              </>
            )}
            
            <Divider sx={{ my: 2 }} />
            <Typography variant="h6" gutterBottom>
              Sorted Features:
            </Typography>
            <Paper 
              variant="outlined" 
              sx={{ 
                maxHeight: 300, 
                overflow: 'auto',
                p: 1
              }}
            >
              <List dense>
                {results.sorted_features.map((feature, index) => (
                  <ListItem key={index}>
                    <ListItemText primary={`${index + 1}. ${feature}`} />
                  </ListItem>
                ))}
              </List>
            </Paper>
          </Paper>
        )}

        {rawContent && (
          <Box sx={{ mt: 4 }}>
            <Paper variant="outlined" sx={{ p: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  {contentType === 'csv' ? 'CSV Content:' : 'Text Content:'}
                </Typography>
                <Button 
                  variant="contained" 
                  color={successCopy ? "success" : "primary"}
                  onClick={handleCopyContent}
                >
                  {successCopy ? "Copied!" : "Copy to Clipboard"}
                </Button>
              </Box>
              <TextField
                multiline
                fullWidth
                variant="outlined"
                value={rawContent}
                InputProps={{
                  readOnly: true,
                  style: { 
                    fontFamily: 'monospace', 
                    whiteSpace: 'pre',
                    maxHeight: '400px',
                    overflow: 'auto'
                  }
                }}
              />
              <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                Since downloads aren't working, you can copy this data and paste it into a text editor or spreadsheet application.
              </Typography>
            </Paper>
          </Box>
        )}

        <Box sx={{ mt: 3 }}>
          <Button 
            variant="outlined" 
            color="info"
            onClick={testApiConnection}
            sx={{ mr: 2 }}
          >
            Test API Connection
          </Button>
        </Box>
      </Box>
    </Container>
  );
}

export default App; 