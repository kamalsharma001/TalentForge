import { useEffect } from 'react'
import { Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/auth/ProtectedRoute'

// Dynamic document title synchronizer
function PageTitleSync() {
  const location = useLocation()

  useEffect(() => {
    const path = location.pathname
    if (path === '/') {
      document.title = 'TalentForge — Interview Management & Preparation'
    } else if (path.startsWith('/candidate/ai-prep/questions')) {
      document.title = 'Practice Questions Studio | TalentForge'
    } else if (path.startsWith('/candidate/ai-prep/report/')) {
      document.title = 'AI Interview Evaluation | TalentForge'
    } else if (path.startsWith('/candidate/ai-prep/mock')) {
      document.title = 'AI Mock Interview | TalentForge'
    } else if (path.startsWith('/candidate/ai-prep')) {
      document.title = 'AI Prep Hub | TalentForge'
    } else if (path.startsWith('/candidate/dashboard')) {
      document.title = 'Candidate Dashboard | TalentForge'
    } else if (path.startsWith('/candidate/interviews')) {
      document.title = 'My Interviews | TalentForge'
    } else if (path.startsWith('/candidate/reports')) {
      document.title = 'Interview Reports | TalentForge'
    } else if (path.startsWith('/candidate/profile')) {
      document.title = 'Candidate Profile | TalentForge'
    } else if (path.startsWith('/candidate/practice')) {
      document.title = 'Practice Questions | TalentForge'
    } else if (path.startsWith('/recruiter/dashboard')) {
      document.title = 'Recruiter Dashboard | TalentForge'
    } else if (path.startsWith('/recruiter/request')) {
      document.title = 'Request Interview | TalentForge'
    } else if (path.startsWith('/recruiter/interviews')) {
      document.title = 'Interviews | TalentForge'
    } else if (path.startsWith('/recruiter/reports')) {
      document.title = 'Reports | TalentForge'
    } else if (path.startsWith('/interviewer/dashboard')) {
      document.title = 'Interviewer Dashboard | TalentForge'
    } else if (path.startsWith('/interviewer/interviews')) {
      document.title = 'Interviews | TalentForge'
    } else if (path.startsWith('/interviewer/schedule')) {
      document.title = 'Availability Schedule | TalentForge'
    } else if (path.startsWith('/interviewer/reports')) {
      document.title = 'Submit Report | TalentForge'
    } else if (path.startsWith('/admin/dashboard')) {
      document.title = 'Admin Dashboard | TalentForge'
    } else if (path.startsWith('/admin/users')) {
      document.title = 'Admin Users | TalentForge'
    } else if (path.startsWith('/admin/interviews')) {
      document.title = 'Admin Interviews | TalentForge'
    } else if (path.includes('/room')) {
      document.title = 'Interview Room | TalentForge'
    } else if (path.startsWith('/login')) {
      document.title = 'Sign In | TalentForge'
    } else if (path.startsWith('/register')) {
      document.title = 'Create Account | TalentForge'
    } else {
      document.title = 'TalentForge — Interview Management & Preparation'
    }
  }, [location.pathname])

  return null
}

// Public pages
import LandingPage from './pages/LandingPage'
import LoginPage from './pages/auth/LoginPage'
import RegisterPage from './pages/auth/RegisterPage'
import AuthCallbackPage from './pages/auth/AuthCallbackPage'

// Recruiter pages
import RecruiterDashboard from './pages/recruiter/RecruiterDashboard'
import RequestInterview from './pages/recruiter/RequestInterview'
import RecruiterInterviews from './pages/recruiter/RecruiterInterviews'
import RecruiterReports from './pages/recruiter/RecruiterReports'

// Interviewer pages
import InterviewerDashboard from './pages/interviewer/InterviewerDashboard'
import InterviewerInterviews from './pages/interviewer/InterviewerInterviews'
import InterviewerSchedule from './pages/interviewer/InterviewerSchedule'
import SubmitReport from './pages/interviewer/SubmitReport'

// Candidate pages
import CandidateDashboard from './pages/candidate/CandidateDashboard'
import CandidateInterviews from './pages/candidate/CandidateInterviews'
import CandidateReports from './pages/candidate/CandidateReports'
import CandidateProfile from './pages/candidate/CandidateProfile'
import MockInterviews from './pages/candidate/MockInterviews'
import MockInterviewSession from './pages/candidate/MockInterviewSession'
import PracticeQuestions from './pages/candidate/PracticeQuestions'

// Candidate AI Prep & Mock pages
import CandidateAiPrepHub from './pages/candidate/CandidateAiPrepHub'
import CandidateAiQuestions from './pages/candidate/CandidateAiQuestions'
import CandidateAiMockSetup from './pages/candidate/CandidateAiMockSetup'
import CandidateAiMockRoom from './pages/candidate/CandidateAiMockRoom'
import CandidateAiReport from './pages/candidate/CandidateAiReport'

// Admin pages
import AdminDashboard from './pages/admin/AdminDashboard'
import AdminUsers from './pages/admin/AdminUsers'
import AdminInterviews from './pages/admin/AdminInterviews'

// Shared pages
import InterviewDetail from './pages/shared/InterviewDetail'
import ReportDetail from './pages/shared/ReportDetail'
import NotificationsPage from './pages/shared/NotificationsPage'
import NotFoundPage from './pages/shared/NotFoundPage'
import InterviewRoom from './pages/shared/InterviewRoom'

export default function App() {
  return (
    <AuthProvider>
      <PageTitleSync />

      <Routes>

        {/* Public */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/auth/callback" element={<AuthCallbackPage />} />

        {/* Recruiter */}
        <Route path="/recruiter" element={<Navigate to="/recruiter/dashboard" replace />} />

        <Route
          path="/recruiter/dashboard"
          element={
            <ProtectedRoute roles={['recruiter','admin']}>
              <RecruiterDashboard />
            </ProtectedRoute>
          }
        />

        <Route
          path="/recruiter/request"
          element={
            <ProtectedRoute roles={['recruiter','admin']}>
              <RequestInterview />
            </ProtectedRoute>
          }
        />

        <Route
          path="/recruiter/interviews"
          element={
            <ProtectedRoute roles={['recruiter','admin']}>
              <RecruiterInterviews />
            </ProtectedRoute>
          }
        />

        <Route
          path="/recruiter/reports"
          element={
            <ProtectedRoute roles={['recruiter','admin']}>
              <RecruiterReports />
            </ProtectedRoute>
          }
        />

        <Route
          path="/recruiter/notifications"
          element={
            <ProtectedRoute roles={['recruiter','admin']}>
              <NotificationsPage />
            </ProtectedRoute>
          }
        />

        {/* Interviewer */}
        <Route path="/interviewer" element={<Navigate to="/interviewer/dashboard" replace />} />

        <Route
          path="/interviewer/dashboard"
          element={
            <ProtectedRoute roles={['interviewer']}>
              <InterviewerDashboard />
            </ProtectedRoute>
          }
        />

        <Route
          path="/interviewer/interviews"
          element={
            <ProtectedRoute roles={['interviewer']}>
              <InterviewerInterviews />
            </ProtectedRoute>
          }
        />

        <Route
          path="/interviewer/schedule"
          element={
            <ProtectedRoute roles={['interviewer']}>
              <InterviewerSchedule />
            </ProtectedRoute>
          }
        />

        <Route
          path="/interviewer/reports"
          element={
            <ProtectedRoute roles={['interviewer']}>
              <SubmitReport />
            </ProtectedRoute>
          }
        />

        <Route
          path="/interviewer/notifications"
          element={
            <ProtectedRoute roles={['interviewer']}>
              <NotificationsPage />
            </ProtectedRoute>
          }
        />

        {/* Candidate */}
        <Route path="/candidate" element={<Navigate to="/candidate/dashboard" replace />} />

        <Route
          path="/candidate/dashboard"
          element={
            <ProtectedRoute roles={['candidate']}>
              <CandidateDashboard />
            </ProtectedRoute>
          }
        />

        <Route
          path="/candidate/interviews"
          element={
            <ProtectedRoute roles={['candidate']}>
              <CandidateInterviews />
            </ProtectedRoute>
          }
        />

        <Route
          path="/candidate/reports"
          element={
            <ProtectedRoute roles={['candidate']}>
              <CandidateReports />
            </ProtectedRoute>
          }
        />

        <Route
          path="/candidate/profile"
          element={
            <ProtectedRoute roles={['candidate']}>
              <CandidateProfile />
            </ProtectedRoute>
          }
        />

        <Route
          path="/candidate/mock-interviews"
          element={
            <ProtectedRoute roles={['candidate']}>
              <MockInterviews />
            </ProtectedRoute>
          }
        />

        <Route
          path="/candidate/mock-interviews/:id"
          element={
            <ProtectedRoute roles={['candidate']}>
              <MockInterviewSession />
            </ProtectedRoute>
          }
        />

        <Route
          path="/candidate/practice"
          element={
            <ProtectedRoute roles={['candidate']}>
              <PracticeQuestions />
            </ProtectedRoute>
          }
        />

        {/* Candidate AI Prep & Mock */}
        <Route
          path="/candidate/ai-prep"
          element={
            <ProtectedRoute roles={['candidate']}>
              <CandidateAiPrepHub />
            </ProtectedRoute>
          }
        />

        <Route
          path="/candidate/ai-prep/questions"
          element={
            <ProtectedRoute roles={['candidate']}>
              <CandidateAiQuestions />
            </ProtectedRoute>
          }
        />

        <Route
          path="/candidate/ai-prep/mock"
          element={
            <ProtectedRoute roles={['candidate']}>
              <CandidateAiMockSetup />
            </ProtectedRoute>
          }
        />

        <Route
          path="/candidate/ai-prep/mock/:id"
          element={
            <ProtectedRoute roles={['candidate']}>
              <CandidateAiMockRoom />
            </ProtectedRoute>
          }
        />

        <Route
          path="/candidate/ai-prep/report/:id"
          element={
            <ProtectedRoute roles={['candidate']}>
              <CandidateAiReport />
            </ProtectedRoute>
          }
        />
        
        <Route
          path="/candidate/notifications"
          element={
            <ProtectedRoute roles={['candidate']}>
              <NotificationsPage />
            </ProtectedRoute>
          }
        />

        {/* Admin */}
        <Route path="/admin" element={<Navigate to="/admin/dashboard" replace />} />

        <Route
          path="/admin/dashboard"
          element={
            <ProtectedRoute roles={['admin']}>
              <AdminDashboard />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/users"
          element={
            <ProtectedRoute roles={['admin']}>
              <AdminUsers />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/interviews"
          element={
            <ProtectedRoute roles={['admin']}>
              <AdminInterviews />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/reports"
          element={
            <ProtectedRoute roles={['admin']}>
              <RecruiterReports />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/notifications"
          element={
            <ProtectedRoute roles={['admin']}>
              <NotificationsPage />
            </ProtectedRoute>
          }
        />


        {/* Shared */}
        <Route
          path="/interviews/:id"
          element={
            <ProtectedRoute>
              <InterviewDetail />
            </ProtectedRoute>
          }
        />

        <Route
          path="/interviews/:id/room"
          element={
            <ProtectedRoute>
              <InterviewRoom />
            </ProtectedRoute>
          }
        />

        <Route
          path="/reports/:interviewId"
          element={
            <ProtectedRoute>
              <ReportDetail />
            </ProtectedRoute>
          }
        />

        {/* Fallback */}
        <Route path="/404" element={<NotFoundPage />} />
        <Route path="*" element={<Navigate to="/404" replace />} />

      </Routes>

    </AuthProvider>
  )
}