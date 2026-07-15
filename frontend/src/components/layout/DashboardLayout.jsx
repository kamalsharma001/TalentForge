import TopNavbar from './TopNavbar'

export default function DashboardLayout({ children }) {
  return (
    <div className="min-h-screen flex flex-col bg-cream-100">
      <TopNavbar />
      <main className="flex-1 p-4 sm:p-6">
        {children}
      </main>
    </div>
  )
}
