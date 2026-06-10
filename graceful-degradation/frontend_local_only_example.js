// Example frontend logic for VSR Graceful Degradation
// The real application can adapt this logic to its own framework.

async function loadConfig() {
  const response = await fetch('/app_config.json', { cache: 'no-store' });
  return await response.json();
}

function disableExternalAssets() {
  console.log('LOCAL_ONLY mode: disabling global CDNs and heavy assets');

  // Example: do not load remote images, video, analytics, maps or CDN scripts.
  document.querySelectorAll('[data-external="true"]').forEach((element) => {
    element.remove();
  });
}

function loadLocalTextData() {
  console.log('Loading core local text and cached data only');
  // Example: fetch('/local/core-data.json')
}

function loadFullFeatures() {
  console.log('Normal mode: loading full application features');
  // Example: load CDN assets, media and global API calls.
}

async function startApplication() {
  const config = await loadConfig();

  if (config.LOCAL_ONLY) {
    disableExternalAssets();
    loadLocalTextData();
  } else {
    loadFullFeatures();
  }
}

startApplication().catch((error) => {
  console.error('App startup failed:', error);
});
