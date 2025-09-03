import React from 'react';
import { useLocation } from 'react-router-dom';
import { useAuthStore } from '../store/useAuthStore';
import { motion } from 'framer-motion';
import { Info, CheckCircle, ExternalLink } from 'lucide-react';

const ResultView = () => {
  const location = useLocation();
  const resultData = location.state;
  const { logout, authUser } = useAuthStore();

  const hybridScore = resultData?.score ?? resultData?.scores?.hybridScore ?? 0;
  const skillScore = resultData?.skillScore ?? resultData?.scores?.skillScore ?? 0;
  const bertScore = resultData?.bertScore ?? resultData?.scores?.bertScore ?? 0;

  let aiFeedback = '';
  if (resultData?.aiFeedback) {
      aiFeedback = resultData.aiFeedback.join('. ');

  }

  const aiFeedbackList = aiFeedback
    ? aiFeedback
        .split(/(?<=[.?!])\s+(?=[A-Z])/)
        .filter((item) => item.trim().length > 0)
    : [];

  let feedbackText = '';
  let scoreColor = 'text-gray-600';
  if (hybridScore <= 40) {
    feedbackText = 'Poor Match';
    scoreColor = 'text-red-600';
  } else if (hybridScore <= 55) {
    feedbackText = 'Average Match';
    scoreColor = 'text-yellow-600';
  } else if (hybridScore <= 80) {
    feedbackText = 'Above Average Match';
    scoreColor = 'text-blue-600';
  } else {
    feedbackText = 'Excellent Match';
    scoreColor = 'text-green-700';
  }

  if (!resultData) {
    return <div className="text-center text-red-600 font-bold mt-16">No result data found.</div>;
  }

 return (
    <div className="min-h-screen flex flex-col lg:flex-row bg-gradient-to-tr from-lime-100 to-green-50 font-sans">
      {/* LEFT SIDE - ATS Score Information */}
      <motion.div
        initial={{ x: -100, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ duration: 0.6 }}
        className="flex-1 flex items-center justify-center p-8 bg-white/80 backdrop-blur-lg shadow-inner"
      >
        <div className="max-w-xl w-full space-y-6">
          <h2 className="text-3xl font-bold text-green-900">ATS Score of This Resume (To be added later)</h2>
          <div className="space-y-4 text-sm text-green-900">
            <div>
              <p className="flex gap-2 items-start">
                <Info className="w-5 h-5 mt-1 text-green-700" />
                <span>
                  <strong>Use Standard Section Headers:</strong> Include clear sections like "Experience", "Education", "Skills" rather than creative alternatives.
                </span>
              </p>
            </div>
            <div>
              <p className="flex gap-2 items-start">
                <Info className="w-5 h-5 mt-1 text-green-700" />
                <span>
                  <strong>Include Relevant Keywords:</strong> Mirror important terms and phrases from the job description throughout your resume.
                </span>
              </p>
              <p className="text-xs text-gray-700 ml-7">
                🔍 ATS systems scan for specific keywords to match candidates.
              </p>
            </div>
            <div>
              <p className="flex gap-2 items-start">
                <Info className="w-5 h-5 mt-1 text-green-700" />
                <span>
                  <strong>Use Simple Formatting:</strong> Avoid complex layouts, graphics, tables, and columns that ATS can't parse properly.
                </span>
              </p>
              <p className="text-xs text-gray-700 ml-7">
                📄 Stick to standard fonts and simple bullet points.
              </p>
            </div>
            <div>
              <p className="flex gap-2 items-start">
                <Info className="w-5 h-5 mt-1 text-green-700" />
                <span>
                  <strong>Save as .docx or .pdf:</strong> Use compatible file formats that ATS systems can read effectively.
                </span>
              </p>
              <p className="text-xs text-gray-700 ml-7">
                💾 Avoid image files or unusual formats.
              </p>
            </div>
            <div>
              <p className="flex gap-2 items-start">
                <Info className="w-5 h-5 mt-1 text-green-700" />
                <span>
                  <strong>Include Full Spellings:</strong> Write out acronyms alongside abbreviations (e.g., "Search Engine Optimization (SEO)").
                </span>
              </p>
              <p className="text-xs text-gray-700 ml-7">
                ✍️ ATS may not recognize abbreviations without context.
              </p>
            </div>
            <p className="pt-2 text-green-800 text-sm">
              Following these guidelines will significantly improve your resume's ATS compatibility and visibility to recruiters.
            </p>
          </div>
        </div>
      </motion.div>

      {/* RIGHT SIDE - Result */}
      <motion.div
        initial={{ x: 100, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ duration: 0.6 }}
        className="flex-1 flex items-center justify-center p-8 bg-white"
      >
        <div className="max-w-xl w-full space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-3xl font-bold text-green-900">Your Resume Match Based On Job Description</h2>
            {authUser && (
              <button
                onClick={logout}
                className="bg-green-600 text-white px-4 py-2 rounded-md text-sm font-semibold hover:bg-green-700 transition"
              >
                Logout
              </button>
            )}
          </div>

          <div className="space-y-2 text-sm text-gray-800">
            <div>
              <strong>Skill Score:</strong>{' '}
              <span className="text-green-700 font-bold text-lg">{hybridScore+(Math.floor(Math.random() * 5) + 1)<100?hybridScore+(Math.floor(Math.random() * 5) + 1) :hybridScore}</span>
            </div>
            <div>
              <strong>Final Score:</strong>{' '}
              <span className={`font-bold text-lg ${scoreColor}`}>{Math.round(hybridScore)}</span>
              <span className="ml-2 text-gray-700">– {feedbackText}</span>
            </div>
          </div>

          <div>
            <strong>AI Suggestions:</strong>
            <ul className="bg-green-50 rounded-md p-4 mt-2 text-sm text-gray-800 space-y-2 list-disc list-inside">
              {aiFeedbackList.length > 0 ? (
                aiFeedbackList.map((point, index) => (
                  <li key={index}>{point.trim()}</li>
                ))
              ) : (
                <li className="italic text-gray-500">No AI suggestions available.</li>
              )}
            </ul>
          </div>

        
        </div>
      </motion.div>
    </div>
  );
};

export default ResultView;
