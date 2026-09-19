const express = require('express');
const cors = require('cors');
const multer = require('multer');
const axios = require('axios');

const app = express();
app.use(cors());
app.use(express.json());

const upload = multer({ dest: 'uploads/' });

// ⚠️ bdel hado b credentials dyal l-Discord Application ta3ek
const CLIENT_ID = 'YOUR_DISCORD_CLIENT_ID';
const CLIENT_SECRET = 'YOUR_DISCORD_CLIENT_SECRET';
const REDIRECT_URI = 'https://grfix-backend-production.up.railway.app/auth/discord/callback';

// 1. Route ta3 Discord Auth Redirection
app.get('/auth/discord', (req, res) => {
    const discordAuthUrl = `https://discord.com/api/oauth2/authorize?client_id=${CLIENT_ID}&redirect_uri=${encodeURIComponent(REDIRECT_URI)}&response_type=code&scope=identify`;
    res.redirect(discordAuthUrl);
});

// 2. Route ta3 Discord Callback
app.get('/auth/discord/callback', async (req, res) => {
    const code = req.query.code;
    if (!code) {
        return res.status(400).send('No code provided from Discord');
    }

    try {
        // Exchange code for token
        const tokenResponse = await axios.post('https://discord.com/api/oauth2/token', new URLSearchParams({
            client_id: CLIENT_ID,
            client_secret: CLIENT_SECRET,
            grant_type: 'authorization_code',
            code: code,
            redirect_uri: REDIRECT_URI,
        }), {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });

        const accessToken = tokenResponse.data.access_token;

        // Get user info
        const userResponse = await axios.get('https://discord.com/api/users/@me', {
            headers: { Authorization: `Bearer ${accessToken}` }
        });

        const userData = encodeURIComponent(JSON.stringify(userResponse.data));
        
        // Redirect back to Netlify frontend with user data
        res.redirect(`https://b7fax.mooo.com/?user=${userData}`); // bdel b rabet Netlify dyalk ila kan mokhtalif
    } catch (error) {
        console.error('Discord Auth Error:', error.response?.data || error.message);
        res.status(500).send('Authentication failed');
    }
});

// 3. API Decrypt Endpoint
app.post('/api/decrypt', upload.single('file'), (req, res) => {
    if (!req.file) {
        return res.status(400).json({ error: 'No file uploaded' });
    }
    //hna t-dir l-mantiq (logic) ta3 fkt chifir
    setTimeout(() => {
        res.json({
            success: true,
            message: 'Decrypted successfully',
            downloadUrl: '#' //hna t-hot link ta3 tahmil l-file l-m-salh
        });
    }, 2000);
});

// 4. API 3D Fix Endpoint
app.post('/api/fix-3d', upload.single('file'), (req, res) => {
    if (!req.file) {
        return res.status(400).json({ error: 'No file uploaded' });
    }
    //hna t-dir l-mantiq ta3 islaḥ 3D
    setTimeout(() => {
        res.json({
            success: true,
            message: '3D Fixed successfully',
            downloadUrl: '#'
        });
    }, 2000);
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});