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
  Switch,
  FormControlLabel,
  Slider
} from '@mui/material';
import './App.css';
import CheckIcon from '@mui/icons-material/Check';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';

const API_URL = '';

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
  const [downloadingPdf, setDownloadingPdf] = useState(false);
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
      
      console.log("API Response:", response.data);
      console.log("Summary present:", Boolean(response.data.summary));
      
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
  
  const handleDirectPdfDownload = async () => {
    if (!text.trim() && !results) {
      setError('Please process some text before downloading PDF');
      return;
    }
    
    setDownloadingPdf(true);
    setError('');
    
    const url = `${API_URL}/api/direct-pdf-download`;
    console.log('Attempting to download PDF from:', url);
    
    try {
      // Use a direct download approach
      const response = await axios.post(url, {
        text: text || "Sample text",
        feature_type: featureType,
        ngram_size: ngramSize,
        base,
        summarize,
        summary_ratio: summaryRatio
      }, {
        responseType: 'blob'  // Important to handle binary data
      });
      
      // Create object URL from the blob response
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const urlObj = window.URL.createObjectURL(blob);
      
      // Extract filename from Content-Disposition header if available
      let filename = 'report.pdf';
      const contentDisposition = response.headers['content-disposition'];
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?([^"]*)"?/);
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1];
        }
      }
      
      // Create download link and trigger it
      const link = document.createElement('a');
      link.href = urlObj;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      
      // Clean up
      setTimeout(() => {
        document.body.removeChild(link);
        window.URL.revokeObjectURL(urlObj);
      }, 100);
      
    } catch (err) {
      console.error('PDF direct download error:', err);
      setError(`Error downloading PDF: ${err.message}`);
        } finally {
      setDownloadingPdf(false);
    }
  };

  const handleDirectExcelDownload = async () => {
    if (!text.trim() && !results) {
      setError('Please process some text before downloading Excel');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      // Use a direct download approach
      const response = await axios.post(`${API_URL}/api/direct-excel-download`, {
        text: text || "Sample text",
        feature_type: featureType,
        ngram_size: ngramSize,
        base,
        summarize,
        summary_ratio: summaryRatio
      }, {
        responseType: 'blob'  // Important to handle binary data
      });
      
      // Create object URL from the blob response
      const blob = new Blob([response.data], { 
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
      });
      const url = window.URL.createObjectURL(blob);
      
      // Extract filename from Content-Disposition header if available
      let filename = 'report.xlsx';
      const contentDisposition = response.headers['content-disposition'];
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?([^"]*)"?/);
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1];
        }
      }
      
      // Create download link and trigger it
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      
      // Clean up
      setTimeout(() => {
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      }, 100);
      
    } catch (err) {
      console.error('Excel direct download error:', err);
      setError(`Error downloading Excel: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleSimpleDownload = async () => {
    try {
      console.log('Attempting simple download test');
      const response = await axios.post(`${API_URL}/api/simple-download`, {
        text: text || "Sample text",
        feature_type: featureType
      }, {
        responseType: 'blob'
      });
      
      // Create a download link
      const blob = new Blob([response.data], { type: 'text/plain' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'test_download.txt');
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err) {
      console.error('Simple download error:', err);
      setError(`Simple download test failed: ${err.message}`);
    }
  };

  const handleCsvDownload = async () => {
    if (!text.trim() && !results) {
      setError('Please process some text before downloading CSV');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      console.log('Downloading CSV from URL:', `${API_URL}/csv`);
      
      const response = await axios.post(`${API_URL}/csv`, {
        text: text || "Sample text",
        feature_type: featureType,
        ngram_size: ngramSize,
        base,
        summarize,
        summary_ratio: summaryRatio
      }, {
        responseType: 'blob'
      });
      
      // Create a download link
      const blob = new Blob([response.data], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      
      // Create and trigger the download link
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'features.csv');
      document.body.appendChild(link);
      link.click();
      
      // Clean up
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
    } catch (err) {
      console.error('CSV download error:', err);
      if (err.response) {
        console.error('Error status:', err.response.status);
        console.error('Error data:', err.response.data);
      }
      setError(`Error downloading CSV: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleTextDownload = async () => {
    try {
      setLoading(true);
      const response = await axios.post(`${API_URL}/api/text`, {
        text: text || "Sample text",
        feature_type: featureType,
        ngram_size: ngramSize,
        base,
        summarize,
        summary_ratio: summaryRatio
      }, {
        responseType: 'blob'
      });
      
      const blob = new Blob([response.data], { type: 'text/plain' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'features.txt');
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err) {
      console.error('Text download error:', err);
      setError(`Error downloading text: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleViewCSV = async () => {
    if (!text.trim() && !results) {
      setError('Please process some text before downloading CSV');
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
      if (err.response) {
        console.error('Response status:', err.response.status);
        console.error('Response data:', err.response.data);
      }
      setError(`Error retrieving CSV content: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleViewText = async () => {
    if (!text.trim() && !results) {
      setError('Please process some text first');
      return;
    }
    
    setLoading(true);
    setError('');
    
    // Log the URL we're about to request
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
      // Log detailed error information
      if (err.response) {
        console.error('Response status:', err.response.status);
        console.error('Response data:', err.response.data);
      }
      setError(`Error retrieving text content: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleCopyContent = () => {
    navigator.clipboard.writeText(rawContent)
      .then(() => {
        setSuccessCopy(true);
        setTimeout(() => setSuccessCopy(false), 2000);
      })
      .catch((err) => {
        console.error('Failed to copy content:', err);
        setError('Failed to copy content to clipboard');
      });
  };

  // Add this function to test basic connectivity
  const testApiConnection = async () => {
    try {
      setLoading(true);
      console.log('Testing API connection at:', `${API_URL}/api/text-test`);
      
      const response = await axios.get(`${API_URL}/api/text-test`);
      console.log('Test response:', response.data);
      
      setRawContent(response.data.content);
      setContentType('text');
      console.log("API test successful:", response.data);
    } catch (err) {
      console.error('API test error:', err);
      
      // Log detailed error information
      if (err.response) {
        console.error('Response status:', err.response.status);
        console.error('Response data:', err.response.data);
        console.error('Response headers:', err.response.headers);
      } else if (err.request) {
        console.error('Request made but no response received:', err.request);
      } else {
        console.error('Error setting up request:', err.message);
      }
      
      setError(`API test failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Add a super simple health check function
  const checkApiHealth = async () => {
    try {
      setLoading(true);
      console.log('Checking API health at:', `${API_URL}/api/health`);
      
      const response = await axios.get(`${API_URL}/api/health`);
      console.log('Health check response:', response.data);
      
      alert(`API is healthy! Response: ${JSON.stringify(response.data)}`);
    } catch (err) {
      console.error('Health check error:', err);
      alert(`API health check failed: ${err.message}`);
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
            Settings
          </Typography>
          
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, mb: 3 }}>
            <FormControl sx={{ minWidth: 200 }}>
              <InputLabel>Feature Type</InputLabel>
              <Select
                value={featureType}
                onChange={(e) => setFeatureType(e.target.value)}
                label="Feature Type"
              >
                <MenuItem value="numbers">Numbers</MenuItem>
                <MenuItem value="words">Words</MenuItem>
                <MenuItem value="sentences">Sentences</MenuItem>
                <MenuItem value="ngrams">N-grams</MenuItem>
              </Select>
            </FormControl>
            
            {featureType === 'ngrams' && (
              <TextField
                label="N-gram Size"
                type="number"
                value={ngramSize}
                onChange={(e) => setNgramSize(Number(e.target.value))}
                sx={{ width: 150 }}
              />
            )}
            
            {featureType === 'numbers' && (
              <TextField
                label="Radix Base"
                type="number"
                value={base}
                onChange={(e) => setBase(Number(e.target.value))}
                sx={{ width: 150 }}
              />
            )}
          </Box>
          
          <Box sx={{ mt: 2 }}>
            <FormControlLabel
              control={
                <Switch
                  checked={summarize}
                  onChange={(e) => setSummarize(e.target.checked)}
                  color="primary"
                />
              }
              label={
                <Typography sx={{ fontWeight: summarize ? 'bold' : 'normal', color: summarize ? 'primary.main' : 'inherit' }}>
                  Generate Text Summary
                </Typography>
              }
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
                  startIcon={successCopy ? <CheckIcon /> : <ContentCopyIcon />}
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

        {/* Add a test button */}
        <Button 
          variant="outlined" 
          color="info"
          onClick={testApiConnection}
          sx={{ ml: 1 }}
        >
          Test API
        </Button>

        {/* Add a simple health check button */}
        <Button 
          variant="outlined" 
          color="error"
          onClick={checkApiHealth}
          sx={{ mt: 2, mb: 2 }}
        >
          Check API Health
        </Button>
      </Box>
    </Container>
  );
}

export default App;
