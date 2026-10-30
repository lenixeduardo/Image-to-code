import test from 'node:test';
import assert from 'node:assert/strict';
import {parseGeometryConfig,inspectBox} from '../scripts/validate_visual_states.mjs';

test('validates config and rejects missing selectors/viewports',()=>{
  const good={viewports:[{width:390,height:844}],states:[{name:'main',mustFit:['main']}]} ;
  assert.equal(parseGeometryConfig(good),good);
  assert.throws(()=>parseGeometryConfig({...good,states:[]}));
  assert.throws(()=>parseGeometryConfig({...good,viewports:[{width:0,height:0}]}));
  assert.throws(()=>parseGeometryConfig({...good,states:[{name:'empty',mustFit:[]}]}));
});
test('clipped frame, clipping in any direction and absent box must fail',()=>{
  const size={width:390,height:844};
  assert.equal(inspectBox({left:0,top:0,right:390,bottom:844,width:390,height:844},size).passed,true);
  for(const box of [null,{left:-50,top:0,right:350,bottom:844,width:400,height:844},
    {left:0,top:0,right:390,bottom:1000,width:390,height:1000},
    {left:0,top:400,right:390,bottom:400,width:390,height:0}]) assert.equal(inspectBox(box,size).passed,false);
});
