import React, { createContext, useState, useEffect } from 'react';

export const AppContext = createContext();

export const AppProvider = ({ children }) => {
  const [activeProject, setActiveProject] = useState(() => {
    const saved = localStorage.getItem('activeProject');
    return saved ? JSON.parse(saved) : null;
  });
  
  const [activeAsset, setActiveAsset] = useState(() => {
    const saved = localStorage.getItem('activeAsset');
    return saved ? JSON.parse(saved) : null;
  });

  const [activeCaseStudy, setActiveCaseStudy] = useState(() => {
    const saved = localStorage.getItem('activeCaseStudy');
    return saved ? JSON.parse(saved) : null;
  });

  useEffect(() => {
    localStorage.setItem('activeProject', JSON.stringify(activeProject));
  }, [activeProject]);

  useEffect(() => {
    localStorage.setItem('activeAsset', JSON.stringify(activeAsset));
  }, [activeAsset]);

  useEffect(() => {
    localStorage.setItem('activeCaseStudy', JSON.stringify(activeCaseStudy));
  }, [activeCaseStudy]);

  return (
    <AppContext.Provider value={{
      activeProject, setActiveProject,
      activeAsset, setActiveAsset,
      activeCaseStudy, setActiveCaseStudy
    }}>
      {children}
    </AppContext.Provider>
  );
};
