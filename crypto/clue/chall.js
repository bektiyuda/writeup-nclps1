const readline = require('readline');
const seedrandom = require('seedrandom');
const bigInt = require('big-integer');

function isPrime(n, k = 10) {
    if (n.leq(1)) return false;
    if (n.leq(3)) return true;
    if (n.mod(2).isZero()) return false;
    let d = n.minus(1);
    while (d.mod(2).isZero()) {
        d = d.divide(2);
    }
    for (let i = 0; i < k; i++) {
        let a = bigInt.randBetween(2, n.minus(2));
        let x = a.modPow(d, n);
        if (x.eq(1) || x.eq(n.minus(1))) continue;
        let continueLoop = false;
        let tempD = d;
        while (tempD.lt(n.minus(1))) {
            x = x.modPow(2, n);
            tempD = tempD.multiply(2);
            if (x.eq(n.minus(1))) {
                continueLoop = true;
                break;
            }
        }
        if (continueLoop) continue;
        return false;
    }
    return true;
}

function generateSeededPrime(bits, seed) {
    const rng = seedrandom(seed);
    process.stdout.write(`[*] Generating ${bits}-bit prime with seed... `);
    while (true) {
        let p = bigInt(1);
        for (let i = 0; i < bits; i++) {
            p = rng() > 0.5 ? p.shiftLeft(1).or(1) : p.shiftLeft(1);
        }
        p = p.or(1);
        if (isPrime(p)) {
            process.stdout.write("Done!\n");
            return p;
        }
    }
}

function generateChallengeData() {
    console.log("[*] Generating challenge parameters, please wait...");
    const randomValues = Array.from(Array(7), Math.random);
    const publicValues = randomValues.slice(0, 5);
    const secretVal6 = randomValues[5];
    const secretVal7 = randomValues[6];
    const primeSeed = secretVal6.toString() + secretVal7.toString();

    const p = generateSeededPrime(256, primeSeed + "p");
    const q = generateSeededPrime(256, primeSeed + "q");

    if (p.eq(q)) {
        console.error("[!!!] p and q are the same! Rerunning...");
        return generateChallengeData();
    }

    const N = p.multiply(q);
    const e = bigInt(65537);
    const flag = ""; // flag redacted
    const m = bigInt.fromArray(Buffer.from(flag, 'utf-8').toJSON().data, 256);
    const c = m.modPow(e, N);
    
    console.log("[+] Challenge ready!\n");

    return { N, e, c, publicValues };
}

async function main() {
    const challengeData = generateChallengeData();

    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout
    });

    const question = (query) => new Promise(resolve => rl.question(query, resolve));
    while (true) {
        console.log("===============================");
        console.log("          MAIN MENU          ");
        console.log("===============================");
        console.log("1. Give the clue");
        console.log("2. Give the flag");
        console.log("3. Exit");
        console.log("===============================");

        const choice = await question("Masukkan pilihan Anda: ");

        switch (choice.trim()) {
            case '1':
                console.log("\n[+] The 5 Cosmic Numbers (clue):");
                console.log(JSON.stringify(challengeData.publicValues, null, 2), "\n");
                break;
            case '2':
                console.log("\n[+] Encrypted Flag and Public Keys:");
                console.log(`N = ${challengeData.N.toString()}`);
                console.log(`e = ${challengeData.e.toString()}`);
                console.log(`c = ${challengeData.c.toString()}\n`);
                break;
            case '3':
                console.log("\n[+] See you!");
                rl.close();
                return;
            default:
                console.log("\n[!] Invalid choice\n");
                break;
        }
    }
}

main();