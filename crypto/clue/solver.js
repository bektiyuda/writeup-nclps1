const seedrandom = require('seedrandom');
const bigInt = require('big-integer');

// same as source code
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

const N = bigInt("15887396264177417605250873134015355221000840933953912887695849516406848790376414747835245059473727919347815116203208647592420123966675130815988458230165131");
const e = bigInt(65537);
const c = bigInt("5089560475769346323083746826614564985736605749064246822234568173137966110489397126520990430822449038000366291523300789763111136460448864045342320523881054");

const secretVal6 =  0.0476178602895343;
const secretVal7 =  0.5713165454001807;

const primeSeed = secretVal6.toString() + secretVal7.toString();

const p = generateSeededPrime(256, primeSeed + "p");
const q = generateSeededPrime(256, primeSeed + "q");
if (p.equals(q)) throw new Error("p == q (unexpected)");

const phi = p.minus(1).multiply(q.minus(1));
const d = e.modInv(phi);

const m = c.modPow(d, p.multiply(q));
const bytes = m.toArray(256).value;
const flag = Buffer.from(bytes).toString('utf8');
console.log({ p: p.toString(), q: q.toString(), flag });
