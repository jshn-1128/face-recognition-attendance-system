import { useLocation } from 'react-router-dom';

const pageTitles: Record<string, string> = {
  '/dashboard': 'Dashboard',
  '/students': 'Students',
  '/attendance': 'Attendance',
  '/reports': 'Reports',
  '/settings': 'Settings',
};

export function Header() {
  const location = useLocation();
  const title = pageTitles[location.pathname] ?? 'Face Recognition Attendance System';

  return (
    <header className="flex h-16 items-center justify-between border-b bg-white px-6">
      <h1 className="text-xl font-semibold text-gray-800">{title}</h1>
      <span className="text-sm text-gray-500">Face Recognition Attendance System</span>
    </header>
  );
}
