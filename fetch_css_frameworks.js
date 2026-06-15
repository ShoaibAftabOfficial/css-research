const https = require('https');
const fs = require('fs');
const path = require('path');

function fetchJsonWithRetry(url, maxRetries = 5) {
    return new Promise(async (resolve) => {
        for (let i = 0; i < maxRetries; i++) {
            try {
                const res = await new Promise((res, rej) => {
                    https.get(url, { headers: { 'User-Agent': 'NodeJS-Script' } }, (response) => {
                        let data = '';
                        response.on('data', chunk => data += chunk);
                        response.on('end', () => res({ status: response.statusCode, data }));
                    }).on('error', rej);
                });

                if (res.status >= 200 && res.status < 300) {
                    return resolve(JSON.parse(res.data));
                } else if (res.status === 404) {
                    return resolve(null);
                } else if (res.status === 429 || res.status >= 500) {
                    await new Promise(r => setTimeout(r, 1000 * (i + 1)));
                } else {
                    return resolve(null);
                }
            } catch (e) {
                await new Promise(r => setTimeout(r, 1000 * (i + 1)));
            }
        }
        resolve(null);
    });
}

function asyncPool(poolLimit, array, iteratorFn) {
    let i = 0;
    const ret = [];
    const executing = [];
    const enqueue = function () {
        if (i === array.length) return Promise.resolve();
        const item = array[i++];
        const p = Promise.resolve().then(() => iteratorFn(item, array));
        ret.push(p);

        let r = Promise.resolve();
        if (poolLimit <= array.length) {
            const e = p.then(() => executing.splice(executing.indexOf(e), 1));
            executing.push(e);
            if (executing.length >= poolLimit) {
                r = Promise.race(executing);
            }
        }
        return r.then(enqueue);
    };
    return enqueue().then(() => Promise.all(ret));
}

function getCleanName(pkgName) {
    let name = pkgName;
    if (name.startsWith('@')) return name.split('/')[0].substring(1);
    name = name.replace(/^(react-|vue-|angular-|svelte-|ng-|ember-|ngx-)/, '');
    name = name.replace(/(-react|-vue|-angular|-svelte|-cli|-core|-theme|-components|-ui|-framework|-animate|-icons)$/, '');
    return name.toLowerCase();
}

async function main() {
    const queries = [
        "keyword:css", "keyword:css keywords:framework", "css framework", "css library",
        "keywords:css-framework", "keywords:css keywords:library", "ui library",
        "ui framework css", "css toolkit", "frontend framework", "stylesheet framework",
        "css ui", "design system css", "css utility", "utility-first css",
        "css grid framework", "responsive css", "keywords:css keywords:ui"
    ];

    console.log("Fetching packages from NPM registry (Max Depth Search with Auto-Retry)...");
    let allPackages = new Set();

    for (const query of queries) {
        let emptyPagesCount = 0;
        for (let page = 0; page < 40; page++) {
            const from = page * 250;
            const url = `https://registry.npmjs.org/-/v1/search?text=${encodeURIComponent(query)}&size=250&from=${from}`;
            const result = await fetchJsonWithRetry(url, 5);

            if (result && result.objects && result.objects.length > 0) {
                result.objects.forEach(obj => {
                    if (obj.package && obj.package.name) allPackages.add(obj.package.name);
                });
                emptyPagesCount = 0;
            } else {
                emptyPagesCount++;
                if (emptyPagesCount >= 3) break;
            }
            await new Promise(r => setTimeout(r, 100)); // Delay to respect API limits
        }
    }

    const uniquePackages = Array.from(allPackages);
    console.log(`Found ${uniquePackages.length} unique packages. Fetching stats via Bulk API...`);

    const unscoped = uniquePackages.filter(p => !p.startsWith('@'));
    const scoped = uniquePackages.filter(p => p.startsWith('@'));
    const packagesWithStats = [];

    // Unscoped Packages (Bulk)
    const chunkSize = 128;
    const chunks = [];
    for (let i = 0; i < unscoped.length; i += chunkSize) {
        chunks.push(unscoped.slice(i, i + chunkSize));
    }

    let processedChunks = 0;
    await asyncPool(50, chunks, async (chunk) => { // Increased pool limit to 50
        const url = `https://api.npmjs.org/downloads/point/last-week/${chunk.join(',')}`;
        const res = await fetchJsonWithRetry(url, 5);
        if (res) {
            for (const pkg of chunk) {
                if (res[pkg] && res[pkg].downloads !== undefined) {
                    packagesWithStats.push({ name: pkg, downloads: res[pkg].downloads });
                }
            }
        }
        processedChunks++;
        if (processedChunks % 10 === 0) console.log(`Processed ${processedChunks}/${chunks.length} bulk chunks...`);
    });

    // Scoped Packages (Individual)
    let processedScoped = 0;
    await asyncPool(100, scoped, async (pkg) => { // Increased pool limit to 100
        const url = `https://api.npmjs.org/downloads/point/last-week/${encodeURIComponent(pkg)}`;
        const res = await fetchJsonWithRetry(url, 5);
        if (res && res.downloads !== undefined) {
            packagesWithStats.push({ name: pkg, downloads: res.downloads });
        }
        processedScoped++;
        if (processedScoped % 200 === 0) console.log(`Processed ${processedScoped}/${scoped.length} scoped packages...`);
    });

    console.log("Sorting and applying strict brand deduplication...");
    packagesWithStats.sort((a, b) => b.downloads - a.downloads);

    const finalPackages = [];
    const acceptedIdentifiers = new Set();

    for (const pkgObj of packagesWithStats) {
        if (pkgObj.downloads < 10000) continue;

        const pkgName = pkgObj.name;
        let org = null;
        if (pkgName.startsWith('@')) org = pkgName.split('/')[0].substring(1).toLowerCase();

        const cleanName = getCleanName(pkgName);
        let skip = false;

        if (org && acceptedIdentifiers.has(org)) skip = true;
        if (acceptedIdentifiers.has(cleanName)) skip = true;
        for (const accepted of acceptedIdentifiers) {
            if (cleanName.startsWith(accepted + '-')) {
                skip = true;
                break;
            }
        }

        if (!skip) {
            finalPackages.push(pkgObj);
            if (org) acceptedIdentifiers.add(org);
            acceptedIdentifiers.add(cleanName);
            acceptedIdentifiers.add(pkgName);
        }
    }

    console.log(`Mission Accomplished: Found ${finalPackages.length} unique frameworks with >= 10,000 downloads.`);

    let mdContent = `# NPM CSS Frameworks & Libraries (10,000+ Downloads)\n\n`;
    mdContent += `This comprehensive list was generated using 18 distinct search queries, deep API pagination, and strict brand deduplication. Every company is listed only once.\n\n`;
    mdContent += `| No. | Framework Name | Weekly Downloads |\n`;
    mdContent += `| :---: | :--- | :---: |\n`;

    finalPackages.forEach((pkg, index) => {
        mdContent += `| ${index + 1} | \`${pkg.name}\` | ${pkg.downloads.toLocaleString()} |\n`;
    });

    const outputPath = path.join(__dirname, 'css_frameworks_list.md');
    fs.writeFileSync(outputPath, mdContent, 'utf-8');
    console.log(`Success! File written to: ${outputPath}`);
}

main().catch(err => console.error(err));
