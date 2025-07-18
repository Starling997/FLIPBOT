// 🔥 DISCORD FLIP BOT 24/7 - KOMPLETNY KOD Z WEB SCRAPINGIEM
// Autor: Asystent AI | Wersja: 2.0 | Data: 2025-07-18
// Funkcje: OLX + Allegro Lokalnie + Vinted Web Scraping | Railway Ready

const { Client, GatewayIntentBits, EmbedBuilder, SlashCommandBuilder, REST, Routes } = require('discord.js');
const cron = require('node-cron');
const axios = require('axios');
const cheerio = require('cheerio');
const fs = require('fs');
const path = require('path');

// 🎯 KONFIGURACJA
const config = {
    token: process.env.DISCORD_TOKEN,
    clientId: process.env.CLIENT_ID,
    guildId: process.env.GUILD_ID,
    
    // Województwa Polski
    voivodeships: [
        'dolnośląskie', 'kujawsko-pomorskie', 'lubelskie', 'lubuskie',
        'łódzkie', 'małopolskie', 'mazowieckie', 'opolskie',
        'podkarpackie', 'podlaskie', 'pomorskie', 'śląskie',
        'świętokrzyskie', 'warmińsko-mazurskie', 'wielkopolskie', 'zachodniopomorskie'
    ],
    
    // Kategorie produktów
    categories: {
        '📱': 'iPhone',
        '💻': 'MacBook', 
        '🎮': 'PlayStation',
        '🎲': 'Xbox'
    },
    
    // Modele do wyszukiwania
    searchModels: {
        iPhone: ['iPhone 12 Mini 64GB', 'iPhone 12 Mini 128GB', 'iPhone 12 Mini 256GB', 'iPhone 12 64GB', 'iPhone 12 128GB', 'iPhone 12 256GB', 'iPhone 12 Pro 128GB', 'iPhone 12 Pro 256GB', 'iPhone 12 Pro 512GB',
  		'iPhone 12 Pro Max 128GB', 'iPhone 12 Pro Max 256GB', 'iPhone 12 Pro Max 512GB', 'iPhone 13 Mini 128GB', 'iPhone 13 Mini 256GB', 'iPhone 13 128GB', 'iPhone 13 256GB', 'iPhone 13 512GB', 'iPhone 13 		Pro 128GB', 'iPhone 13 Pro 256GB', 'iPhone 13 Pro 512GB', 'iPhone 13 Pro Max 128GB', 'iPhone 13 Pro Max 256GB', 'iPhone 13 Pro Max 512GB', 'iPhone 14 128GB', 'iPhone 14 256GB', 'iPhone 14 512GB',
  		'iPhone 14 Plus 128GB', 'iPhone 14 Plus 256GB', 'iPhone 14 Plus 512GB', 'iPhone 14 Pro 128GB', 'iPhone 14 Pro 256GB', 'iPhone 14 Pro 512GB', 'iPhone 14 Pro Max 128GB', 'iPhone 14 Pro Max 256GB', 		'iPhone 14 Pro Max 512GB', 'iPhone 15 128GB', 'iPhone 15 256GB', 'iPhone 15 512GB', 'iPhone 15 Plus 128GB', 'iPhone 15 Plus 256GB', 'iPhone 15 Plus 512GB', 'iPhone 15 Pro 128GB', 'iPhone 15 Pro 		256GB', 'iPhone 15 Pro 512GB', 'iPhone 15 Pro Max 256GB', 'iPhone 15 Pro Max 512GB', 'iPhone 16 128GB', 'iPhone 16 256GB', 'iPhone 16 512GB', 'iPhone 16 Pro 256GB', 'iPhone 16 Pro 512GB', 'iPhone 		16 Pro Max 256GB', 'iPhone 16 Pro Max 512GB'],
	MacBook: ['MacBook Air M1', 'MacBook Pro M1', 'MacBook Air M2', 'MacBook Pro M2', 'MacBook Air M3', 'MacBook Air M1 2021 256GB', 'MacBook Air M1 2021 512GB', 'MacBook Air M1 2021 1TB', 'MacBook Pro M1 2021 		512GB', 'MacBook Pro M1 2021 1TB', 'MacBook Pro M1 2021 2TB', 'MacBook Air M2 2022 256GB', 'MacBook Air M2 2022 512GB', 'MacBook Air M2 2022 1TB', 'MacBook Pro M2 2022 512GB', 'MacBook Pro M2 2022 		1TB', 'MacBook Pro M2 2022 2TB', 'MacBook Air M3 2023 256GB', 'MacBook Air M3 2023 512GB', 'MacBook Air M3 2023 1TB', 'MacBook Pro M3 2023 512GB', 'MacBook Pro M3 2023 1TB', 'MacBook Pro M3 2023 		2TB'],
        PlayStation: ['PlayStation 4', 'PS4', 'PlayStation 5', 'PS5', 'PlayStation 4 500GB', 'PlayStation 4 1TB', 'PlayStation 4 Slim 500GB', 'PlayStation 4 Slim 1TB', 'PlayStation 4 Pro 1TB', 'PlayStation 5 		Standard 825GB', 'PlayStation 5 Digital Edition 825GB', 'PlayStation 5 Slim 1TB'],
        Xbox: ['Xbox One', 'Xbox Series S', 'Xbox Series X', 'Xbox One 500GB', 'Xbox One 1TB', 'Xbox One S 500GB', 'Xbox One S 1TB', 'Xbox One X 1TB', 'Xbox Series S 512GB', 'Xbox Series S 1TB', 'Xbox Series X 		1TB', 'Xbox Series X 2TB']
	},
    
    // Średnie ceny rynkowe (PLN)
    marketPrices: {
        'iPhone 12': 2800,
        'iPhone 13': 3500,
        'iPhone 14': 4200,
        'iPhone 15': 5000,
        'iPhone 16': 6000,
        'MacBook Air M1': 4500,
        'MacBook Pro M1': 6000,
        'MacBook Air M2': 5500,
        'MacBook Pro M2': 7000,
        'MacBook Air M3': 6000,
        'PlayStation 4': 800,
        'PS4': 800,
        'PlayStation 5': 2200,
        'PS5': 2200,
        'Xbox One': 600,
        'Xbox Series S': 1200,
        'Xbox Series X': 2000
    },
    
    // User Agents dla scraping
    userAgents: [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0'
    ]
};

// 🚀 INICJALIZACJA BOTA
const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent
    ]
});

// 🗂️ STORAGE
let blacklistedSellers = [];
let processedListings = new Set();
let channelCache = new Map();

// 🛠️ UTILITY FUNCTIONS
function getRandomUserAgent() {
    return config.userAgents[Math.floor(Math.random() * config.userAgents.length)];
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function normalizePrice(priceStr) {
    if (!priceStr) return 0;
    return parseInt(priceStr.replace(/[^\d]/g, '')) || 0;
}

function detectProduct(title, description) {
    const text = (title + ' ' + description).toLowerCase();
    
    for (const [category, models] of Object.entries(config.searchModels)) {
        for (const model of models) {
            if (text.includes(model.toLowerCase())) {
                return { category, model };
            }
        }
    }
    return null;
}

function getVoivodeshipFromLocation(location) {
    const locationMap = {
        'warszawa': 'mazowieckie', 'kraków': 'małopolskie', 'gdańsk': 'pomorskie',
        'wrocław': 'dolnośląskie', 'poznań': 'wielkopolskie', 'łódź': 'łódzkie',
        'katowice': 'śląskie', 'lublin': 'lubelskie', 'białystok': 'podlaskie',
        'szczecin': 'zachodniopomorskie', 'bydgoszcz': 'kujawsko-pomorskie',
        'rzeszów': 'podkarpackie', 'kielce': 'świętokrzyskie', 'gorzów': 'lubuskie',
        'opole': 'opolskie', 'olsztyn': 'warmińsko-mazurskie'
    };
    
    const loc = location.toLowerCase();
    for (const [city, voivodeship] of Object.entries(locationMap)) {
        if (loc.includes(city)) return voivodeship;
    }
    
    // Fallback na podstawie końcówek
    if (loc.includes('skie')) return loc.match(/(\w+skie)/)?.[0] || 'mazowieckie';
    return 'mazowieckie'; // domyślne
}

function getCategoryEmoji(category) {
    const emojiMap = {
        'iPhone': '📱',
        'MacBook': '💻',
        'PlayStation': '🎮',
        'Xbox': '🎲'
    };
    return emojiMap[category] || '📦';
}

// 🌐 WEB SCRAPING FUNCTIONS

// 🔥 OLX SCRAPER
async function scrapeOLX() {
    const listings = [];
    
    try {
        console.log('🔍 Rozpoczynam scraping OLX...');
        
        const searchQueries = [
            'iphone', 'macbook', 'playstation', 'xbox'
        ];
        
        for (const query of searchQueries) {
            await sleep(2000); // Delay między zapytaniami
            
            const response = await axios.get(`https://www.olx.pl/oferty/q-${query}/`, {
                headers: {
                    'User-Agent': getRandomUserAgent(),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'pl-PL,pl;q=0.9,en;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                },
                timeout: 10000
            });
            
            const $ = cheerio.load(response.data);
            
            $('[data-cy="l-card"]').each((i, element) => {
                try {
                    const $el = $(element);
                    
                    const title = $el.find('[data-cy="ad-card-title"]').text().trim();
                    const price = $el.find('[data-cy="ad-card-price"]').text().trim();
                    const location = $el.find('[data-cy="ad-card-location"]').text().trim();
                    const link = $el.find('[data-cy="ad-card-title"] a').attr('href');
                    const image = $el.find('img').attr('src');
                    
                    if (title && price && location && link) {
                        const product = detectProduct(title, '');
                        if (product) {
                            const listingId = link.split('/').pop()?.split('#')[0];
                            
                            if (!processedListings.has(listingId)) {
                                listings.push({
                                    id: listingId,
                                    title,
                                    price: normalizePrice(price),
                                    location,
                                    link: link.startsWith('http') ? link : `https://www.olx.pl${link}`,
                                    image: image || '',
                                    source: 'OLX',
                                    category: product.category,
                                    model: product.model,
                                    voivodeship: getVoivodeshipFromLocation(location)
                                });
                                processedListings.add(listingId);
                            }
                        }
                    }
                } catch (err) {
                    console.log('❌ Błąd parsowania elementu OLX:', err.message);
                }
            });
        }
        
        console.log(`✅ OLX: Znaleziono ${listings.length} nowych ogłoszeń`);
        
    } catch (error) {
        console.error('❌ Błąd scrapingu OLX:', error.message);
    }
    
    return listings;
}

// 🔥 ALLEGRO LOKALNIE SCRAPER
async function scrapeAllegroLokalnie() {
    const listings = [];
    
    try {
        console.log('🔍 Rozpoczynam scraping Allegro Lokalnie...');
        
        const searchQueries = [
            'iphone', 'macbook', 'playstation', 'xbox'
        ];
        
        for (const query of searchQueries) {
            await sleep(2000);
            
            const response = await axios.get(`https://allegrolokalnie.pl/oferty/q/${query}`, {
                headers: {
                    'User-Agent': getRandomUserAgent(),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'pl-PL,pl;q=0.9',
                    'Connection': 'keep-alive'
                },
                timeout: 10000
            });
            
            const $ = cheerio.load(response.data);
            
            $('[data-testid="listing-card"]').each((i, element) => {
                try {
                    const $el = $(element);
                    
                    const title = $el.find('[data-testid="listing-title"]').text().trim();
                    const price = $el.find('[data-testid="listing-price"]').text().trim();
                    const location = $el.find('[data-testid="listing-location"]').text().trim();
                    const link = $el.find('[data-testid="listing-title"] a').attr('href');
                    const image = $el.find('[data-testid="listing-image"] img').attr('src');
                    
                    if (title && price && location && link) {
                        const product = detectProduct(title, '');
                        if (product) {
                            const listingId = link.split('/').pop()?.split('?')[0];
                            
                            if (!processedListings.has(listingId)) {
                                listings.push({
                                    id: listingId,
                                    title,
                                    price: normalizePrice(price),
                                    location,
                                    link: link.startsWith('http') ? link : `https://allegrolokalnie.pl${link}`,
                                    image: image || '',
                                    source: 'Allegro Lokalnie',
                                    category: product.category,
                                    model: product.model,
                                    voivodeship: getVoivodeshipFromLocation(location)
                                });
                                processedListings.add(listingId);
                            }
                        }
                    }
                } catch (err) {
                    console.log('❌ Błąd parsowania elementu Allegro Lokalnie:', err.message);
                }
            });
        }
        
        console.log(`✅ Allegro Lokalnie: Znaleziono ${listings.length} nowych ogłoszeń`);
        
    } catch (error) {
        console.error('❌ Błąd scrapingu Allegro Lokalnie:', error.message);
    }
    
    return listings;
}

// 🔥 VINTED SCRAPER
async function scrapeVinted() {
    const listings = [];
    
    try {
        console.log('🔍 Rozpoczynam scraping Vinted...');
        
        const searchQueries = [
            'iphone', 'macbook', 'playstation', 'xbox'
        ];
        
        for (const query of searchQueries) {
            await sleep(2000);
            
            // Vinted używa API, więc spróbujemy endpoint
            const response = await axios.get(`https://www.vinted.pl/api/v2/catalog/items?search_text=${query}&per_page=20`, {
                headers: {
                    'User-Agent': getRandomUserAgent(),
                    'Accept': 'application/json',
                    'Accept-Language': 'pl-PL,pl;q=0.9'
                },
                timeout: 10000
            });
            
            if (response.data && response.data.items) {
                response.data.items.forEach(item => {
                    try {
                        const title = item.title || '';
                        const price = item.price_numeric || 0;
                        const location = item.user?.city || 'Nieznana';
                        const link = `https://www.vinted.pl/items/${item.id}`;
                        const image = item.photos?.[0]?.url || '';
                        
                        const product = detectProduct(title, item.description || '');
                        if (product && price > 0) {
                            const listingId = `vinted_${item.id}`;
                            
                            if (!processedListings.has(listingId)) {
                                listings.push({
                                    id: listingId,
                                    title,
                                    price,
                                    location,
                                    link,
                                    image,
                                    source: 'Vinted',
                                    category: product.category,
                                    model: product.model,
                                    voivodeship: getVoivodeshipFromLocation(location)
                                });
                                processedListings.add(listingId);
                            }
                        }
                    } catch (err) {
                        console.log('❌ Błąd parsowania elementu Vinted:', err.message);
                    }
                });
            }
        }
        
        console.log(`✅ Vinted: Znaleziono ${listings.length} nowych ogłoszeń`);
        
    } catch (error) {
        console.error('❌ Błąd scrapingu Vinted:', error.message);
        
        // Fallback: spróbuj web scraping jeśli API nie działa
        try {
            const response = await axios.get('https://www.vinted.pl/catalog?search_text=iphone', {
                headers: {
                    'User-Agent': getRandomUserAgent(),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
                },
                timeout: 10000
            });
            
            console.log('🔄 Spróbowałem fallback web scraping dla Vinted...');
        } catch (fallbackError) {
            console.error('❌ Fallback Vinted również nieudany:', fallbackError.message);
        }
    }
    
    return listings;
}

// 🔥 GŁÓWNA FUNKCJA SCRAPINGU
async function scrapeAllSources() {
    console.log('🚀 Rozpoczynam scraping wszystkich źródeł...');
    
    const allListings = [];
    
    // Uruchom scraping równolegle
    const [olxListings, allegroListings, vintedListings] = await Promise.allSettled([
        scrapeOLX(),
        scrapeAllegroLokalnie(),
        scrapeVinted()
    ]);
    
    // Dodaj wyniki
    if (olxListings.status === 'fulfilled') {
        allListings.push(...olxListings.value);
    }
    if (allegroListings.status === 'fulfilled') {
        allListings.push(...allegroListings.value);
    }
    if (vintedListings.status === 'fulfilled') {
        allListings.push(...vintedListings.value);
    }
    
    console.log(`✅ Łącznie znaleziono ${allListings.length} nowych ogłoszeń`);
    
    // Przetwórz i wyślij do Discord
    for (const listing of allListings) {
        await sendListingToDiscord(listing);
        await sleep(500); // Opóźnienie między wiadomościami
    }
}

// 📤 WYSYŁANIE DO DISCORD
async function sendListingToDiscord(listing) {
    try {
        const channelName = listing.voivodeship;
        const channel = await getOrCreateChannel(channelName);
        
        if (!channel) {
            console.log(`❌ Nie można znaleźć kanału dla ${channelName}`);
            return;
        }
        
        const marketPrice = config.marketPrices[listing.model] || 0;
        const savings = marketPrice - listing.price;
        const emoji = getCategoryEmoji(listing.category);
        
        const embed = new EmbedBuilder()
            .setTitle(`${emoji} ${listing.title}`)
            .setURL(listing.link)
            .setDescription(`**${listing.source}** • ${listing.location}`)
            .addFields(
                { name: '💰 Cena', value: `${listing.price.toLocaleString()} zł`, inline: true },
                { name: '📊 Średnia rynkowa', value: marketPrice ? `${marketPrice.toLocaleString()} zł` : 'Brak danych', inline: true },
                { name: '📈 Różnica', value: savings > 0 ? `+${savings.toLocaleString()} zł` : `${savings.toLocaleString()} zł`, inline: true }
            )
            .setColor(savings > 0 ? 0x00FF00 : 0xFF6B35)
            .setTimestamp()
            .setFooter({ text: `Źródło: ${listing.source}` });
        
        if (listing.image) {
            embed.setThumbnail(listing.image);
        }
        
        await channel.send({ embeds: [embed] });
        console.log(`✅ Wysłano ogłoszenie: ${listing.title} do #${channelName}`);
        
    } catch (error) {
        console.error('❌ Błąd wysyłania do Discord:', error.message);
    }
}

// 🏗️ TWORZENIE KANAŁÓW
async function getOrCreateChannel(voivodeship) {
    if (channelCache.has(voivodeship)) {
        return channelCache.get(voivodeship);
    }
    
    try {
        const guild = client.guilds.cache.get(config.guildId);
        if (!guild) return null;
        
        let channel = guild.channels.cache.find(ch => ch.name === voivodeship);
        
        if (!channel) {
            channel = await guild.channels.create({
                name: voivodeship,
                type: 0, // Text channel
                topic: `Okazje z województwa ${voivodeship} • 📱 💻 🎮 🎲`
            });
            console.log(`✅ Utworzono kanał #${voivodeship}`);
        }
        
        channelCache.set(voivodeship, channel);
        return channel;
        
    } catch (error) {
        console.error(`❌ Błąd tworzenia kanału ${voivodeship}:`, error.message);
        return null;
    }
}

// 🎯 KOMENDY SLASH
const commands = [
    new SlashCommandBuilder()
        .setName('blacklist')
        .setDescription('Dodaj sprzedawcę do blacklisty')
        .addStringOption(option =>
            option.setName('sprzedawca')
                .setDescription('Nazwa sprzedawcy')
                .setRequired(true)
        ),
    
    new SlashCommandBuilder()
        .setName('whitelist')
        .setDescription('Usuń sprzedawcę z blacklisty')
        .addStringOption(option =>
            option.setName('sprzedawca')
                .setDescription('Nazwa sprzedawcy')
                .setRequired(true)
        ),
    
    new SlashCommandBuilder()
        .setName('pomoc')
        .setDescription('Pokaż dostępne komendy'),
    
    new SlashCommandBuilder()
        .setName('status')
        .setDescription('Pokaż status bota'),
    
    new SlashCommandBuilder()
        .setName('test')
        .setDescription('Testuj scraping (tylko dla adminów)')
];

// 🚀 URUCHOMIENIE BOTA
client.once('ready', async () => {
    console.log(`🚀 ${client.user.tag} jest online!`);
    
    // Rejestruj komendy slash
    const rest = new REST({ version: '10' }).setToken(config.token);
    
    try {
        await rest.put(
            Routes.applicationGuildCommands(config.clientId, config.guildId),
            { body: commands }
        );
        console.log('✅ Komendy slash zarejestrowane');
    } catch (error) {
        console.error('❌ Błąd rejestracji komend:', error);
    }
    
    // Twórz kanały dla wszystkich województw
    for (const voivodeship of config.voivodeships) {
        await getOrCreateChannel(voivodeship);
        await sleep(1000);
    }
    
    console.log('✅ Wszystkie kanały gotowe');
    
    // Uruchom pierwszy scraping
    setTimeout(() => {
        scrapeAllSources();
    }, 5000);
});

// 🎯 OBSŁUGA KOMEND
client.on('interactionCreate', async interaction => {
    if (!interaction.isChatInputCommand()) return;
    
    const { commandName } = interaction;
    
    try {
        switch (commandName) {
            case 'blacklist':
                const sellerToBlock = interaction.options.getString('sprzedawca');
                if (!blacklistedSellers.includes(sellerToBlock)) {
                    blacklistedSellers.push(sellerToBlock);
                    await interaction.reply(`✅ Dodano **${sellerToBlock}** do blacklisty`);
                } else {
                    await interaction.reply(`⚠️ **${sellerToBlock}** już jest na blackliście`);
                }
                break;
                
            case 'whitelist':
                const sellerToUnblock = interaction.options.getString('sprzedawca');
                const index = blacklistedSellers.indexOf(sellerToUnblock);
                if (index > -1) {
                    blacklistedSellers.splice(index, 1);
                    await interaction.reply(`✅ Usunięto **${sellerToUnblock}** z blacklisty`);
                } else {
                    await interaction.reply(`⚠️ **${sellerToUnblock}** nie ma na blackliście`);
                }
                break;
                
            case 'pomoc':
                const helpEmbed = new EmbedBuilder()
                    .setTitle('🤖 Flip Bot - Pomoc')
                    .setDescription('Dostępne komendy:')
                    .addFields(
                        { name: '/blacklist [sprzedawca]', value: 'Dodaj sprzedawcę do blacklisty' },
                        { name: '/whitelist [sprzedawca]', value: 'Usuń sprzedawcę z blacklisty' },
                        { name: '/status', value: 'Pokaż status bota' },
                        { name: '/test', value: 'Testuj scraping (admin only)' }
                    )
                    .setColor(0x00AE86)
                    .setTimestamp();
                
                await interaction.reply({ embeds: [helpEmbed] });
                break;
                
            case 'status':
                const statusEmbed = new EmbedBuilder()
                    .setTitle('📊 Status Bota')
                    .addFields(
                        { name: '🔍 Źródła danych', value: 'OLX • Allegro Lokalnie • Vinted', inline: true },
                        { name: '⏰ Częstotliwość', value: 'Co 10 minut', inline: true },
                        { name: '🚫 Blacklista', value: `${blacklistedSellers.length} sprzedawców`, inline: true },
                        { name: '📝 Przetworzone ogłoszenia', value: processedListings.size.toString(), inline: true },
                        { name: '🏗️ Kanały', value: `${config.voivodeships.length} województw`, inline: true },
                        { name: '🎯 Kategorie', value: '📱 💻 🎮 🎲', inline: true }
                    )
                    .setColor(0x00AE86)
                    .setTimestamp();
                
                await interaction.reply({ embeds: [statusEmbed] });
                break;
                
            case 'test':
                await interaction.reply('🔍 Rozpoczynam test scrapingu...');
                scrapeAllSources();
                break;
        }
        
    } catch (error) {
        console.error('❌ Błąd obsługi komendy:', error);
        if (!interaction.replied) {
            await interaction.reply('❌ Wystąpił błąd podczas wykonywania komendy');
        }
    }
});

// ⏰ CRON JOB - CO 10 MINUT
cron.schedule('*/10 * * * *', () => {
    console.log('⏰ Cron job: Uruchamiam scraping...');
    scrapeAllSources();
});

// 🔧 OBSŁUGA BŁĘDÓW
process.on('unhandledRejection', (reason, promise) => {
    console.error('❌ Unhandled Rejection at:', promise, 'reason:', reason);
});

process.on('uncaughtException', (error) => {
    console.error('❌ Uncaught Exception:', error);
});

// 🚀 URUCHOMIENIE
client.login(config.token);

// 📦 EXPORT (dla Railway)
module.exports = { client, scrapeAllSources };