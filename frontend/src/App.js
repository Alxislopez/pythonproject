import { useState } from "react";

export default function App() {
    const [file, setFile] = useState(null);
    const [processing, setProcessing] = useState(false);
    const [downloadUrl, setDownloadUrl] = useState(null);
    const [error, setError] = useState(null);

    const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "http://127.0.0.1:8000";

    const handleFileChange = (event) => {
        setFile(event.target.files[0]);
        setDownloadUrl(null); // Reset download link on new file upload
        setError(null); // Clear previous errors
    };

    const handleUpload = async () => {
        if (!file) {
            setError("Please select a file first!");
            return;
        }

        setProcessing(true);
        setError(null);

        const formData = new FormData();
        formData.append("file", file);

        try {
            const response = await fetch(`${BACKEND_URL}/process`, {
                method: "POST",
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Server Error: ${response.statusText}`);
            }

            const data = await response.json();
            setDownloadUrl(`${BACKEND_URL}${data.download_url}`);
        } catch (error) {
            console.error("Error processing file:", error);
            setError("Failed to process file. Please try again.");
            setFile(null); // Reset file input on error
        } finally {
            setProcessing(false);
        }
    };

    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-6">
            <div className="bg-white p-6 rounded-lg shadow-lg w-full max-w-md text-center">
                <h2 className="text-xl font-bold mb-4">NLP Text Processor</h2>

                <input
                    type="file"
                    accept=".txt,.pdf"
                    onChange={handleFileChange}
                    className="mb-4 border p-2 w-full"
                />
                <p className="text-sm text-gray-500">Accepted Formats: .txt, .pdf</p>

                {error && <p className="text-red-500 text-sm mt-2" aria-live="polite">{error}</p>}

                <button
                    onClick={handleUpload}
                    disabled={processing}
                    className="mt-4 bg-blue-500 text-white px-4 py-2 rounded-lg disabled:bg-gray-400 flex items-center justify-center"
                >
                    {processing ? "Processing..." : "Upload & Process"}
                </button>

                {downloadUrl && (
                    <a
                        href={downloadUrl}
                        download
                        className="mt-4 block bg-green-500 text-white px-4 py-2 rounded-lg"
                    >
                        See Results & Download
                    </a>
                )}
            </div>
        </div>
    );
}
