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

const API_URL = 'http://localhost:8000/api';

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

  const handleTextSubmit = async () => {
    if (!text.trim()) {
      setError('Please enter some text to process');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post(`${API_URL}/process`, {
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
      const response = await axios.post(`${API_URL}/upload-file`, formData, {
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
  
  const handleDownloadPdf = async () => {
    if (!text.trim() && !results) {
      setError('Please process some text before downloading PDF');
      return;
    }
    
    setDownloadingPdf(true);
    setError('');
    
    try {
      const response = await axios.post(`${API_URL}/download-pdf`, {
        text: text,
        feature_type: featureType,
        ngram_size: ngramSize,
        base,
        summarize,
        summary_ratio: summaryRatio
      }, {
        responseType: 'blob'
      });
      
      // Create a download link and trigger it
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'nlp_processing_results.pdf');
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      setError(`Error generating PDF: ${err.message}`);
    } finally {
      setDownloadingPdf(false);
    }
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ my: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom align="center">
          NLP Text Processor
        </Typography>
        <Typography variant="h6" gutterBottom align="center">
          Process text using optimized Radix Sort
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
              <Button 
                variant="contained" 
                color="primary"
                onClick={handleDownloadPdf}
                disabled={downloadingPdf}
                startIcon={downloadingPdf ? <CircularProgress size={20} /> : null}
              >
                Download as PDF
              </Button>
            </Box>
            
            <Box sx={{ mb: 2 }}>
              <Typography><strong>Processing Time:</strong> {results.processing_time.toFixed(4)} seconds</Typography>
              <Typography><strong>Features Processed:</strong> {results.feature_count}</Typography>
              <Typography><strong>Sorting Method:</strong> Optimized Radix Sort (Base: {base})</Typography>
            </Box>
            
            {results.summary && (
              <>
                <Divider sx={{ my: 2 }} />
                <Typography variant="h6" gutterBottom>
                  Text Summary:
                </Typography>
                <Paper 
                  variant="outlined" 
                  sx={{ p: 2, mb: 3, bgcolor: '#f5f5f5' }}
                >
                  <Typography>{results.summary}</Typography>
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
      </Box>
    </Container>
  );
}

export default App;
