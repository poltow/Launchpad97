/**
 * Launchpad95 Manual - Main JavaScript
 */

// Current selected mode for diagram
let currentMode = 'session';

// Mode configurations with button mappings
const modeConfigs = {
    session: {
        name: 'Session Mode',
        channel: 0,
        topButtons: [
            { label: 'Up', color: 'green', tooltip: 'Navigate scenes up' },
            { label: 'Down', color: 'green', tooltip: 'Navigate scenes down' },
            { label: 'Left', color: 'green', tooltip: 'Navigate tracks left' },
            { label: 'Right', color: 'green', tooltip: 'Navigate tracks right' },
            { label: 'Session', color: 'amber', tooltip: 'Session mode (active) - press again for Pro Session' },
            { label: 'User 1', color: 'off', tooltip: 'Switch to User 1 mode' },
            { label: 'User 2', color: 'off', tooltip: 'Switch to User 2 mode' },
            { label: 'Mixer', color: 'off', tooltip: 'Switch to Mixer mode' }
        ],
        sideButtons: [
            { label: 'Scene 1', color: 'green', tooltip: 'Launch scene 1' },
            { label: 'Scene 2', color: 'green', tooltip: 'Launch scene 2' },
            { label: 'Scene 3', color: 'green', tooltip: 'Launch scene 3' },
            { label: 'Scene 4', color: 'green', tooltip: 'Launch scene 4' },
            { label: 'Scene 5', color: 'green', tooltip: 'Launch scene 5' },
            { label: 'Scene 6', color: 'green', tooltip: 'Launch scene 6' },
            { label: 'Scene 7', color: 'green', tooltip: 'Launch scene 7' },
            { label: 'Scene 8', color: 'green', tooltip: 'Launch scene 8' }
        ],
        matrixDescription: 'Clip launch grid - 8x8 clips'
    },
    prosession: {
        name: 'Pro Session Mode',
        channel: 0,
        topButtons: [
            { label: 'Up', color: 'green', tooltip: 'Navigate scenes up' },
            { label: 'Down', color: 'green', tooltip: 'Navigate scenes down' },
            { label: 'Left', color: 'green', tooltip: 'Navigate tracks left' },
            { label: 'Right', color: 'green', tooltip: 'Navigate tracks right' },
            { label: 'Session', color: 'green', tooltip: 'Pro Session mode (active) - press for zoom view' },
            { label: 'User 1', color: 'off', tooltip: 'Switch to User 1 mode' },
            { label: 'User 2', color: 'off', tooltip: 'Switch to User 2 mode' },
            { label: 'Mixer', color: 'off', tooltip: 'Switch to Mixer mode' }
        ],
        sideButtons: [
            { label: 'Undo', color: 'amber', tooltip: 'Undo (long: Redo)' },
            { label: 'Shift', color: 'amber', tooltip: 'Shift + clip = select, + bottom = launch quantize' },
            { label: 'Click', color: 'green', tooltip: 'Copy/Paste clips, double-tap = metronome' },
            { label: 'Quant', color: 'green', tooltip: 'Hold + clip = quantize, double = rec quant toggle' },
            { label: 'Double', color: 'green', tooltip: 'Double loop, double-tap = fixed length toggle' },
            { label: 'Delete', color: 'red', tooltip: 'Delete clip, double-tap = unmute all' },
            { label: 'Dup', color: 'amber', tooltip: 'Duplicate clip, double-tap = unsolo all' },
            { label: 'Rec', color: 'red', tooltip: 'Hold + slot = record, press = session rec' }
        ],
        matrixDescription: 'Clip grid with modifier actions - hold side button + tap clip'
    },
    instrument: {
        name: 'Instrument Mode',
        channel: 11,
        topButtons: [
            { label: 'Prev Scene', color: 'green', tooltip: 'Previous scene' },
            { label: 'Next Scene', color: 'green', tooltip: 'Next scene' },
            { label: 'Prev Track', color: 'green', tooltip: 'Previous track' },
            { label: 'Next Track', color: 'green', tooltip: 'Next track' },
            { label: 'Session', color: 'off', tooltip: 'Switch to Session mode' },
            { label: 'User 1', color: 'amber', tooltip: 'Instrument mode (active)' },
            { label: 'User 2', color: 'off', tooltip: 'Switch to User 2 mode' },
            { label: 'Mixer', color: 'off', tooltip: 'Switch to Mixer mode' }
        ],
        sideButtons: [
            { label: 'Scale', color: 'amber', tooltip: 'Enter scale selection mode' },
            { label: 'Undo', color: 'amber', tooltip: 'Undo (long press: Redo)' },
            { label: 'Oct +', color: 'green', tooltip: 'Octave up' },
            { label: 'Oct -', color: 'green', tooltip: 'Octave down' },
            { label: 'Stop', color: 'red', tooltip: 'Stop clip (long press: Delete)' },
            { label: 'Play', color: 'red', tooltip: 'Play/fire clip' },
            { label: 'Solo', color: 'amber', tooltip: 'Solo track (long press: Mute)' },
            { label: 'Rec', color: 'red', tooltip: 'Session record' }
        ],
        matrixDescription: 'Scale-based note playing grid'
    },
    device: {
        name: 'Device Controller',
        channel: 3,
        topButtons: [
            { label: 'Device +', color: 'red', tooltip: 'Next device' },
            { label: 'Device -', color: 'red', tooltip: 'Previous device' },
            { label: 'Track -', color: 'red', tooltip: 'Previous track' },
            { label: 'Track +', color: 'red', tooltip: 'Next track' },
            { label: 'Session', color: 'off', tooltip: 'Switch to Session mode' },
            { label: 'User 1', color: 'green', tooltip: 'Device mode (active)' },
            { label: 'User 2', color: 'off', tooltip: 'Switch to User 2 mode' },
            { label: 'Mixer', color: 'off', tooltip: 'Switch to Mixer mode' }
        ],
        sideButtons: [
            { label: 'On/Off', color: 'red', tooltip: 'Toggle device on/off' },
            { label: 'Bank +', color: 'green', tooltip: 'Next parameter bank' },
            { label: 'Bank -', color: 'green', tooltip: 'Previous parameter bank' },
            { label: 'Precision', color: 'amber', tooltip: 'Toggle precision mode' },
            { label: 'Lock 1', color: 'amber', tooltip: 'Device lock slot 1' },
            { label: 'Lock 2', color: 'amber', tooltip: 'Device lock slot 2' },
            { label: 'Lock 3', color: 'amber', tooltip: 'Device lock slot 3' },
            { label: 'Lock 4', color: 'amber', tooltip: 'Device lock slot 4' }
        ],
        matrixDescription: '8 parameter sliders (columns)'
    },
    drumseq: {
        name: 'Drum Step Sequencer',
        channel: 1,
        topButtons: [
            { label: 'Prev Scene', color: 'green', tooltip: 'Previous scene' },
            { label: 'Next Scene', color: 'green', tooltip: 'Next scene' },
            { label: 'Prev Track', color: 'green', tooltip: 'Previous track' },
            { label: 'Next Track', color: 'green', tooltip: 'Next track' },
            { label: 'Session', color: 'off', tooltip: 'Switch to Session mode' },
            { label: 'User 1', color: 'off', tooltip: 'Switch to User 1 mode' },
            { label: 'User 2', color: 'amber', tooltip: 'Drum sequencer (active)' },
            { label: 'Mixer', color: 'off', tooltip: 'Switch to Mixer mode' }
        ],
        sideButtons: [
            { label: 'Scale', color: 'amber', tooltip: 'Scale selection overlay' },
            { label: 'Lock', color: 'red', tooltip: 'Lock to clip/track' },
            { label: 'Quant', color: 'amber', tooltip: 'Cycle quantization (1/4, 1/8, 1/16, 1/32)' },
            { label: 'Mode', color: 'amber', tooltip: 'Toggle combined/multinote mode' },
            { label: 'Up', color: 'green', tooltip: 'Scroll notes up' },
            { label: 'Down', color: 'green', tooltip: 'Scroll notes down' },
            { label: 'Velocity', color: 'green', tooltip: 'Velocity shift/cycle' },
            { label: 'Mute', color: 'red', tooltip: 'Mute shift' }
        ],
        matrixDescription: 'Combined: Note selector + Loop selector + Note editor'
    },
    melodicseq: {
        name: 'Melodic Step Sequencer',
        channel: 2,
        topButtons: [
            { label: 'Prev Scene', color: 'green', tooltip: 'Previous scene' },
            { label: 'Next Scene', color: 'green', tooltip: 'Next scene' },
            { label: 'Prev Track', color: 'green', tooltip: 'Previous track' },
            { label: 'Next Track', color: 'green', tooltip: 'Next track' },
            { label: 'Session', color: 'off', tooltip: 'Switch to Session mode' },
            { label: 'User 1', color: 'off', tooltip: 'Switch to User 1 mode' },
            { label: 'User 2', color: 'green', tooltip: 'Melodic sequencer (active)' },
            { label: 'Mixer', color: 'off', tooltip: 'Switch to Mixer mode' }
        ],
        sideButtons: [
            { label: 'Scale', color: 'amber', tooltip: 'Scale selection' },
            { label: 'Lock', color: 'red', tooltip: 'Lock to clip' },
            { label: 'Quant', color: 'amber', tooltip: 'Quantization' },
            { label: 'Random', color: 'green', tooltip: 'Randomize current parameter' },
            { label: 'Length', color: 'amber', tooltip: 'Edit note lengths' },
            { label: 'Octave', color: 'red', tooltip: 'Edit octaves' },
            { label: 'Velocity', color: 'red', tooltip: 'Edit velocities' },
            { label: 'Notes', color: 'green', tooltip: 'Edit note pitches' }
        ],
        matrixDescription: '7-row polyphonic note editor + page selector'
    },
    mixer: {
        name: 'Mixer Mode',
        channel: 6,
        topButtons: [
            { label: 'Prev Scene', color: 'green', tooltip: 'Previous scene' },
            { label: 'Next Scene', color: 'green', tooltip: 'Next scene' },
            { label: 'Prev Track', color: 'green', tooltip: 'Previous track' },
            { label: 'Next Track', color: 'green', tooltip: 'Next track' },
            { label: 'Session', color: 'off', tooltip: 'Switch to Session mode' },
            { label: 'User 1', color: 'off', tooltip: 'Switch to User 1 mode' },
            { label: 'User 2', color: 'off', tooltip: 'Switch to User 2 mode' },
            { label: 'Mixer', color: 'amber', tooltip: 'Mixer mode (active)' }
        ],
        sideButtons: [
            { label: 'Volume', color: 'green', tooltip: 'Volume mode' },
            { label: 'Pan', color: 'green', tooltip: 'Pan mode' },
            { label: 'Send A', color: 'green', tooltip: 'Send A mode' },
            { label: 'Send B', color: 'green', tooltip: 'Send B mode' },
            { label: 'Stop All', color: 'red', tooltip: 'Stop all clips' },
            { label: 'Mute All', color: 'amber', tooltip: 'Unmute all tracks' },
            { label: 'Solo All', color: 'red', tooltip: 'Unsolo all tracks' },
            { label: 'Arm All', color: 'red', tooltip: 'Unarm all tracks' }
        ],
        matrixDescription: 'Overview: Vol/Pan/Send rows + Stop/Mute/Solo/Arm'
    }
};

// Musical scales data - all 34 scales
const scales = [
    // Original 26 scales
    { name: 'Major', intervals: [0, 2, 4, 5, 7, 9, 11], description: 'Ionian mode - most common Western scale' },
    { name: 'Minor', intervals: [0, 2, 3, 5, 7, 8, 10], description: 'Natural minor / Aeolian mode' },
    { name: 'Dorian', intervals: [0, 2, 3, 5, 7, 9, 10], description: 'Minor with raised 6th - jazz, funk' },
    { name: 'Mixolydian', intervals: [0, 2, 4, 5, 7, 9, 10], description: 'Major with flat 7th - rock, blues' },
    { name: 'Lydian', intervals: [0, 2, 4, 6, 7, 9, 11], description: 'Major with raised 4th - dreamy' },
    { name: 'Phrygian', intervals: [0, 1, 3, 5, 7, 8, 10], description: 'Minor with flat 2nd - Spanish, metal' },
    { name: 'Locrian', intervals: [0, 1, 3, 5, 6, 8, 10], description: 'Diminished mode - unstable, tense' },
    { name: 'Diminished', intervals: [0, 1, 3, 4, 6, 7, 9, 10], description: 'Half-whole diminished - jazz' },
    { name: 'Whole-half', intervals: [0, 2, 3, 5, 6, 8, 9, 11], description: 'Whole-half diminished' },
    { name: 'Whole Tone', intervals: [0, 2, 4, 6, 8, 10], description: 'All whole steps - impressionist' },
    { name: 'Minor Blues', intervals: [0, 3, 5, 6, 7, 10], description: 'Blues scale with blue notes' },
    { name: 'Minor Pentatonic', intervals: [0, 3, 5, 7, 10], description: 'Five-note minor - rock, pop' },
    { name: 'Major Pentatonic', intervals: [0, 2, 4, 7, 9], description: 'Five-note major - folk, country' },
    { name: 'Harmonic Minor', intervals: [0, 2, 3, 5, 7, 8, 11], description: 'Minor with raised 7th - classical' },
    { name: 'Melodic Minor', intervals: [0, 2, 3, 5, 7, 9, 11], description: 'Jazz melodic minor' },
    { name: 'Super Locrian', intervals: [0, 1, 3, 4, 6, 8, 10], description: 'Altered scale - jazz dominant' },
    { name: 'Bhairav', intervals: [0, 1, 4, 5, 7, 8, 11], description: 'Indian classical raga' },
    { name: 'Hungarian Minor', intervals: [0, 2, 3, 6, 7, 8, 11], description: 'Double harmonic minor' },
    { name: 'Minor Gypsy', intervals: [0, 1, 4, 5, 7, 8, 10], description: 'Eastern European gypsy' },
    { name: 'Hirojoshi', intervals: [0, 2, 3, 7, 8], description: 'Japanese pentatonic' },
    { name: 'In-Sen', intervals: [0, 1, 5, 7, 10], description: 'Japanese scale - melancholic' },
    { name: 'Iwato', intervals: [0, 1, 5, 6, 10], description: 'Japanese scale - dark' },
    { name: 'Kumoi', intervals: [0, 2, 3, 7, 9], description: 'Japanese pentatonic - koto' },
    { name: 'Pelog', intervals: [0, 1, 3, 4, 7, 8], description: 'Indonesian gamelan' },
    { name: 'Spanish', intervals: [0, 1, 3, 4, 5, 6, 8, 10], description: 'Phrygian dominant - flamenco' },
    { name: 'IonEol', intervals: [0, 2, 3, 4, 5, 7, 8, 9, 10, 11], description: 'Combined Major/Minor' },
    // New scales (v2.0)
    { name: 'Arabic', intervals: [0, 1, 4, 5, 7, 8, 11], description: 'Double harmonic major - Middle Eastern' },
    { name: 'Japanese', intervals: [0, 1, 5, 7, 8], description: 'Hirajoshi variant - traditional' },
    { name: 'Enigmatic', intervals: [0, 1, 4, 6, 8, 10, 11], description: 'Verdi\'s enigmatic scale' },
    { name: 'Neapolitan', intervals: [0, 1, 3, 5, 7, 9, 11], description: 'Neapolitan major - dramatic' },
    { name: 'Persian', intervals: [0, 1, 4, 5, 6, 8, 11], description: 'Persian classical music' },
    { name: 'Algerian', intervals: [0, 2, 3, 5, 6, 7, 8, 11], description: 'North African - exotic' },
    { name: 'Acoustic', intervals: [0, 2, 4, 6, 7, 9, 10], description: 'Lydian dominant - overtone series' },
    { name: 'Blues Major', intervals: [0, 2, 3, 4, 7, 9], description: 'Major blues scale - bright blues' }
];

// DOM Ready
document.addEventListener('DOMContentLoaded', function() {
    initNavigation();
    initSearch();
    initModeSelector();
    initSmoothScroll();
    highlightCurrentSection();
});

// Initialize navigation
function initNavigation() {
    const menuToggle = document.querySelector('.menu-toggle');
    const sidebar = document.querySelector('.sidebar');

    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', () => {
            sidebar.classList.toggle('open');
        });

        // Close sidebar when clicking outside
        document.addEventListener('click', (e) => {
            if (!sidebar.contains(e.target) && !menuToggle.contains(e.target)) {
                sidebar.classList.remove('open');
            }
        });
    }
}

// Initialize search
function initSearch() {
    const searchInput = document.querySelector('.search-input');
    if (!searchInput) return;

    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase();
        const sections = document.querySelectorAll('.main-content section');

        sections.forEach(section => {
            const text = section.textContent.toLowerCase();
            if (query && !text.includes(query)) {
                section.style.display = 'none';
            } else {
                section.style.display = '';
            }
        });
    });
}

// Initialize mode selector for interactive diagram
function initModeSelector() {
    const modeButtons = document.querySelectorAll('.mode-selector button');

    modeButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            modeButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentMode = btn.dataset.mode;
            updateDiagram(currentMode);
        });
    });
}

// Update the Launchpad diagram based on selected mode
function updateDiagram(mode) {
    const config = modeConfigs[mode];
    if (!config) return;

    // Update top buttons
    const topButtons = document.querySelectorAll('.lp-btn.top');
    topButtons.forEach((btn, i) => {
        if (config.topButtons[i]) {
            btn.className = `lp-btn top ${config.topButtons[i].color}`;
            btn.textContent = config.topButtons[i].label;
            btn.dataset.tooltip = config.topButtons[i].tooltip;
        }
    });

    // Update side buttons
    const sideButtons = document.querySelectorAll('.lp-btn.side');
    sideButtons.forEach((btn, i) => {
        if (config.sideButtons[i]) {
            btn.className = `lp-btn side ${config.sideButtons[i].color}`;
            btn.textContent = config.sideButtons[i].label;
            btn.dataset.tooltip = config.sideButtons[i].tooltip;
        }
    });

    // Update mode name display
    const modeNameEl = document.querySelector('.current-mode-name');
    if (modeNameEl) {
        modeNameEl.textContent = config.name;
    }

    // Update MIDI channel display
    const channelEl = document.querySelector('.current-channel');
    if (channelEl) {
        channelEl.textContent = `MIDI Channel: ${config.channel}`;
    }

    // Update matrix description
    const matrixDescEl = document.querySelector('.matrix-description');
    if (matrixDescEl) {
        matrixDescEl.textContent = config.matrixDescription;
    }
}

// Smooth scroll for anchor links
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
}

// Highlight current section in sidebar
function highlightCurrentSection() {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.sidebar-nav a');

    window.addEventListener('scroll', () => {
        let current = '';

        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            if (pageYOffset >= sectionTop - 100) {
                current = section.getAttribute('id');
            }
        });

        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${current}`) {
                link.classList.add('active');
            }
        });
    });
}

// Generate scale reference table
function generateScaleTable() {
    const container = document.getElementById('scale-table-container');
    if (!container) return;

    let html = '<table><thead><tr><th>#</th><th>Scale</th><th>Intervals</th><th>Description</th></tr></thead><tbody>';

    scales.forEach((scale, index) => {
        html += `<tr>
            <td>${index}</td>
            <td><strong>${scale.name}</strong></td>
            <td><code>${scale.intervals.join(', ')}</code></td>
            <td>${scale.description}</td>
        </tr>`;
    });

    html += '</tbody></table>';
    container.innerHTML = html;
}

// Copy code block to clipboard
function copyCode(button) {
    const codeBlock = button.parentElement.querySelector('code');
    if (codeBlock) {
        navigator.clipboard.writeText(codeBlock.textContent);
        button.textContent = 'Copied!';
        setTimeout(() => {
            button.textContent = 'Copy';
        }, 2000);
    }
}

// Export for use in HTML
window.Launchpad95Manual = {
    modeConfigs,
    scales,
    updateDiagram,
    generateScaleTable,
    copyCode
};
