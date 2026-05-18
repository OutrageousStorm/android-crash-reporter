#!/usr/bin/env node
/**
 * crash_collector.js -- Collect Android crashes from logcat in real-time
 * Usage: node crash_collector.js [--save crashes.json] [--filter app.package]
 */
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

class CrashCollector {
    constructor(options = {}) {
        this.crashes = [];
        this.anrs = [];
        this.filter = options.filter || null;
        this.outputFile = options.save || null;
    }

    start() {
        console.log('🐛 Android Crash Collector — Press Ctrl+C to stop\n');
        
        const process = exec('adb logcat -v brief', (err) => {
            if (err) console.error('ADB error:', err);
        });

        let buffer = '';
        process.stdout.on('data', (chunk) => {
            buffer += chunk;
            const lines = buffer.split('\n');
            buffer = lines.pop(); // Keep incomplete line

            lines.forEach(line => this.analyzeLine(line));
        });

        process.on('exit', () => this.printSummary());
    }

    analyzeLine(line) {
        // Check for crashes
        if (line.includes('FATAL EXCEPTION') || line.includes('CRASH')) {
            const match = line.match(/(\S+)\s+\d+/);
            const pkg = match ? match[1] : 'unknown';
            if (this.filter && !pkg.includes(this.filter)) return;

            this.crashes.push({
                timestamp: new Date().toISOString(),
                package: pkg,
                line: line,
                type: 'CRASH'
            });
            console.log(`[CRASH] ${pkg}: ${line.substring(0, 80)}`);
        }

        // Check for ANR
        if (line.includes('ANR') || line.includes('Application Not Responding')) {
            const match = line.match(/(\S+)\s+\d+/);
            const pkg = match ? match[1] : 'unknown';
            if (this.filter && !pkg.includes(this.filter)) return;

            this.anrs.push({
                timestamp: new Date().toISOString(),
                package: pkg,
                line: line,
                type: 'ANR'
            });
            console.log(`[ANR] ${pkg}: ${line.substring(0, 80)}`);
        }

        // Check for OOM
        if (line.includes('OutOfMemory') || line.includes('No space left')) {
            const match = line.match(/(\S+)\s+\d+/);
            const pkg = match ? match[1] : 'unknown';
            if (this.filter && !pkg.includes(this.filter)) return;

            console.log(`[OOM] ${pkg}: ${line.substring(0, 80)}`);
        }
    }

    printSummary() {
        console.log('\n═══════════════════════════════════════');
        console.log(`📊 Crash Report Summary`);
        console.log(`Crashes: ${this.crashes.length}`);
        console.log(`ANRs: ${this.anrs.length}`);

        if (this.outputFile) {
            fs.writeFileSync(this.outputFile, JSON.stringify({
                collected_at: new Date().toISOString(),
                total_crashes: this.crashes.length,
                total_anrs: this.anrs.length,
                crashes: this.crashes,
                anrs: this.anrs
            }, null, 2));
            console.log(`✅ Saved to ${this.outputFile}`);
        }
    }
}

const args = process.argv.slice(2);
const options = {
    save: args.includes('--save') ? args[args.indexOf('--save') + 1] : null,
    filter: args.includes('--filter') ? args[args.indexOf('--filter') + 1] : null,
};

const collector = new CrashCollector(options);
collector.start();
