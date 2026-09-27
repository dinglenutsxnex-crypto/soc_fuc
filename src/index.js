export default {
  async fetch(req) {
    const u = new URL(req.url);
    if (u.pathname === '/auth') {
      try { await req.arrayBuffer(); } catch (e) {}
      return new Response('Success', {
        status: 200,
        headers: { 'Content-Type': 'text/plain' },
      });
    }
    return new Response('sfapi', { status: 200 });
  },
};
