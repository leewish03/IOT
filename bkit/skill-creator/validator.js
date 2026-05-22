#!/usr/bin/env node
/**
 * Skill Validator
 * @module skill-creator/validator
 * @version 1.6.0
 *
 * Validates existing skill structure and frontmatter completeness.
 */

const fs = require('fs');
const path = require('path');

const SKILLS_DIR = path.join(__dirname, '..', 'skills');

const REQUIRED_FRONTMATTER = [
  'name',
  'description',
  'classification',
  'deprecation-risk'
];

const VALID_CLASSIFICATIONS = ['workflow', 'capability', 'hybrid'];
const VALID_RISKS = ['none', 'low', 'medium', 'high'];

/**
 * Validate a skill's SKILL.md
 * @param {string} skillName - Skill name
 * @returns {{ valid: boolean, errors: string[], warnings: string[] }}
 */
function validateSkill(skillName) {
  const errors = [];
  const warnings = [];

  const skillPath = path.join(SKILLS_DIR, skillName, 'SKILL.md');

  if (!fs.existsSync(skillPath)) {
    return { valid: false, errors: [`SKILL.md not found: ${skillPath}`], warnings };
  }

  const content = fs.readFileSync(skillPath, 'utf8');
  const fmMatch = content.match(/^---\r?\n([\s\S]*?)\r?\n---/);

  if (!fmMatch) {
    return { valid: false, errors: ['No YAML frontmatter found'], warnings };
  }

  const frontmatter = fmMatch[1];

  // Check required fields
  for (const field of REQUIRED_FRONTMATTER) {
    if (!frontmatter.includes(`${field}:`)) {
      errors.push(`Missing required field: ${field}`);
    }
  }

  // Validate classification value
  const clsMatch = frontmatter.match(/classification:\s*(\w+)/);
  if (clsMatch && !VALID_CLASSIFICATIONS.includes(clsMatch[1])) {
    errors.push(`Invalid classification: ${clsMatch[1]} (expected: ${VALID_CLASSIFICATIONS.join('|')})`);
  }

  // Validate deprecation-risk value
  const riskMatch = frontmatter.match(/deprecation-risk:\s*(\w+)/);
  if (riskMatch && !VALID_RISKS.includes(riskMatch[1])) {
    errors.push(`Invalid deprecation-risk: ${riskMatch[1]} (expected: ${VALID_RISKS.join('|')})`);
  }

  // Check for eval definition
  const evalDirs = ['workflow', 'capability', 'hybrid'];
  let hasEval = false;
  for (const dir of evalDirs) {
    const evalPath = path.join(__dirname, '..', 'evals', dir, skillName, 'eval.yaml');
    if (fs.existsSync(evalPath)) {
      hasEval = true;
      break;
    }
  }
  if (!hasEval) {
    warnings.push('No eval.yaml found for this skill');
  }

  return { valid: errors.length === 0, errors, warnings };
}

/**
 * Validate all skills
 * @returns {Object} Validation summary
 */
function validateAllSkills() {
  const results = {};
  const dirs = fs.readdirSync(SKILLS_DIR).filter(d =>
    fs.statSync(path.join(SKILLS_DIR, d)).isDirectory()
  );

  for (const dir of dirs) {
    results[dir] = validateSkill(dir);
  }

  const total = Object.keys(results).length;
  const valid = Object.values(results).filter(r => r.valid).length;

  return { total, valid, invalid: total - valid, results };
}

// CLI execution
if (require.main === module) {
  const args = process.argv.slice(2);

  if (args.includes('--all')) {
    const summary = validateAllSkills();
    console.log(`Validation: ${summary.valid}/${summary.total} skills valid`);
    for (const [skill, result] of Object.entries(summary.results)) {
      if (!result.valid) {
        console.log(`  FAIL: ${skill} - ${result.errors.join(', ')}`);
      }
    }
  } else {
    const skillIdx = args.indexOf('--skill');
    const skillName = skillIdx >= 0 ? args[skillIdx + 1] : null;
    if (!skillName) {
      console.log('Usage: node validator.js --skill <name> | --all');
      process.exit(1);
    }
    const result = validateSkill(skillName);
    console.log(JSON.stringify(result, null, 2));
  }
}

module.exports = { validateSkill, validateAllSkills };
