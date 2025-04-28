import React from "react";

const MainLayout = ({ children }) => {
  return (
    <div className="flex h-screen overflow-hidden bg-gray-100 dark:bg-gray-900">
      {/* Le contenu sera injecté ici - généralement la sidebar et la zone de contenu principale */}
      {children}
    </div>
  );
};

export default MainLayout;
