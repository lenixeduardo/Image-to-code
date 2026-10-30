#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
const [positive, negative] = process.argv.slice(2);
assert(positive && negative, 'Provide positive and negative capture report paths');
const good=JSON.parse(fs.readFileSync(positive,'utf8'));
const bad=JSON.parse(fs.readFileSync(negative,'utf8'));
assert.equal(good.passed, true, JSON.stringify(good.warnings));
assert.equal(good.captures.length, 5, 'Mobile, tablet, desktop, same-viewport and smoke viewport expected');
for(const c of good.captures){
  assert.equal(c.status,200);
  assert.equal(c.horizontalOverflow,false);
  assert.equal(c.missingMain,false);
  assert.deepEqual(c.brokenImages,[]);
  assert.deepEqual(c.unlabeledControls,[]);
  assert.deepEqual(c.runtimeErrors,[]);
  assert.deepEqual(c.failedRequests,[]);
  if(c.screenshot)assert(fs.existsSync(path.join(path.dirname(path.resolve(positive)),c.screenshot)), `Missing screenshot ${c.screenshot}`);
}
assert.equal(bad.passed,false,'Broken image must be a failure');
assert(bad.captures.some(c=>c.brokenImages?.length || c.failedRequests?.length), 'Failure must identify broken resource');
console.log('PASS browser positive/negative integration evidence');
