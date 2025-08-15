
import { useEffect, useState } from 'react';

const Header = () => {
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    setLoaded(true);
  }, []);

  return (
    <header className={`py-8 transition-opacity duration-700 ${loaded ? 'opacity-100' : 'opacity-0'}`}>
      <h1 className="font-bold text-white text-3xl md:text-4xl tracking-widest text-center" style={{ fontFamily: 'Arial', letterSpacing: '0.2em' }}>
        ENGINE ARCADE
      </h1>
    </header>
  );
};

export default Header;
