import test from 'node:test';
import assert from 'node:assert/strict';
import { parseArgs, viewport, inspectResult, DEFAULT_VIEWPORTS } from '../scripts/capture.mjs';

test('default sizes and reference viewport', () => {
  assert.deepEqual(DEFAULT_VIEWPORTS.mobile, { width: 390, height: 844 });
  const args = parseArgs(['--url', 'http://localhost:3000', '--reference-viewport', '1179x616', '--smoke-widths', '360,430,360']);
  assert.deepEqual(args.reference, { width: 1179, height: 616 });
  assert.deepEqual(args.smokeWidths, [360, 430]);
});
test('malformed arguments and unsafe protocols rejected', () => {
  assert.throws(() => viewport('100x80'));
  assert.throws(() => viewport('hello'));
  assert.throws(() => parseArgs(['--url', 'file:///test.html']));
  assert.throws(() => parseArgs(['--url', 'http://localhost', '--smoke-widths', '300,nope']));
  assert.throws(() => parseArgs(['--url', 'http://localhost', '--reference-viewport']));
});
test('browser quality failures are not reported as successful', () => {
  assert.equal(inspectResult({ status: 200, horizontalOverflow: false, runtimeErrors: [], brokenImages: [], unlabeledControls: [], missingMain: false }), false);
  for (const failure of [
    { horizontalOverflow: true }, { runtimeErrors: ['boom'] }, { brokenImages: ['missing.png'] },
    { unlabeledControls: ['button'] }, { status: 404 }, { missingMain: true },
  ]) assert.equal(inspectResult({ status: 200, ...failure }), true);
});
