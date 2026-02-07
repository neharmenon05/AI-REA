import React, { useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';

// Translation dictionary
const TEXT_MAP = {
  // Navbar
  'Home': 'nav.home',
  'Dashboard': 'nav.dashboard',
  'Marketplace': 'nav.marketplace',
  'About': 'nav.about',
  'Login': 'nav.login',
  'Register': 'nav.register',
  'Logout': 'nav.logout',
  
  // Dashboard
  'Property Analysis Dashboard': 'dashboard.title',
  'Describe the property you want to analyze': 'dashboard.subtitle',
  'Kindly mention the number of rooms, area, and square feet of property': 'dashboard.description',
  'Analyze Property': 'dashboard.analyze',
  
  // Results
  'Property Analysis Results': 'results.title',
  'Back to Dashboard': 'results.back',
  'Export PDF': 'results.export',
  
  // Marketplace
  'Property Marketplace': 'marketplace.title',
  'Find Properties →': 'marketplace.findProperties',
  'List Property →': 'marketplace.listProperty',
  'List Your Property': 'marketplace.sell.title',
  'Available Properties': 'marketplace.buy.title',
  
  // Common
  'Loading...': 'common.loading',
  'Send': 'assistant.send',
};

const AutoTranslate = ({ children }) => {
  const { t, i18n } = useTranslation();
  const isTranslating = useRef(false);

  useEffect(() => {
    const translatePage = () => {
      if (isTranslating.current) return;
      isTranslating.current = true;

      try {
        const walker = document.createTreeWalker(
          document.body,
          NodeFilter.SHOW_TEXT,
          {
            acceptNode: (node) => {
              const parent = node.parentElement;
              if (!parent || parent.tagName === 'SCRIPT' || parent.tagName === 'STYLE') return NodeFilter.FILTER_REJECT;

              const text = node.nodeValue?.trim();
              if (!text) return NodeFilter.FILTER_REJECT;

              return NodeFilter.FILTER_ACCEPT;
            }
          }
        );

        let node;
        while (node = walker.nextNode()) {
          // Save original text if not saved yet
          if (!node.parentElement.getAttribute('data-i18n-original')) {
            node.parentElement.setAttribute('data-i18n-original', node.nodeValue);
          }
          const originalText = node.parentElement.getAttribute('data-i18n-original').trim();

          if (TEXT_MAP[originalText]) {
            node.nodeValue = t(TEXT_MAP[originalText]);
          }
        }

        // Translate placeholders
        document.querySelectorAll('input[placeholder], textarea[placeholder]').forEach(el => {
          if (!el.getAttribute('data-i18n-placeholder')) {
            el.setAttribute('data-i18n-placeholder', el.placeholder);
          }
          const original = el.getAttribute('data-i18n-placeholder');
          if (TEXT_MAP[original]) {
            el.placeholder = t(TEXT_MAP[original]);
          }
        });

      } finally {
        isTranslating.current = false;
      }
    };

    // Initial translation
    const timer = setTimeout(translatePage, 100);

    // On language change
    const handleLanguageChange = () => {
      setTimeout(translatePage, 100);
    };

    i18n.on('languageChanged', handleLanguageChange);

    return () => {
      clearTimeout(timer);
      i18n.off('languageChanged', handleLanguageChange);
    };
  }, [t, i18n]);

  return <>{children}</>;
};

export default AutoTranslate;
