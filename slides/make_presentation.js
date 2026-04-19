const pptxgen = require('pptxgenjs');
const { safeOuterShadow } = require('/home/oai/skills/slides/pptxgenjs_helpers');

const pptx = new pptxgen();
pptx.layout = 'LAYOUT_WIDE';
pptx.author = 'OpenAI';
pptx.company = 'OpenAI';
pptx.subject = 'Coursework presentation';
pptx.title = 'Book Metadata and Recommendation API';
pptx.lang = 'en-GB';
theme();

function theme() {
  pptx.theme = {
    headFontFace: 'Aptos Display',
    bodyFontFace: 'Aptos',
    lang: 'en-GB'
  };
}

function addHeader(slide, title, subtitle='') {
  slide.addShape(pptx.ShapeType.rect, {x:0, y:0, w:13.333, h:0.65, fill:{color:'0F172A'}, line:{color:'0F172A'}});
  slide.addText(title, {x:0.45, y:0.16, w:8.8, h:0.24, color:'FFFFFF', bold:true, fontSize:24});
  if (subtitle) slide.addText(subtitle, {x:0.46, y:0.9, w:12.1, h:0.25, color:'475569', fontSize:11});
}

function addFooter(slide, num) {
  slide.addText(`${num}`, {x:12.75, y:7.0, w:0.25, h:0.2, fontSize:9, color:'64748B', align:'right'});
}

function addBulletList(slide, items, x, y, w, h, fontSize=18) {
  slide.addText(items.map(t=>({text:t, options:{bullet:{indent:16}}})), {x,y,w,h,fontSize,color:'0F172A', breakLine:true, paraSpaceAfterPt:10, valign:'top'});
}

// Slide 1
{
  const s = pptx.addSlide();
  s.background = { color: 'F8FAFC' };
  s.addShape(pptx.ShapeType.roundRect, {x:0.65,y:0.85,w:12.05,h:5.6,rectRadius:0.08,fill:{color:'E2E8F0'},line:{color:'E2E8F0'}});
  s.addShape(pptx.ShapeType.rect, {x:0.65,y:0.85,w:12.05,h:1.2,fill:{color:'0F172A'},line:{color:'0F172A'}});
  s.addText('Book Metadata and Recommendation API', {x:1.0,y:1.55,w:8.8,h:0.7,fontSize:26,bold:true,color:'0F172A'});
  s.addText('XJCO3011 Coursework 1 - oral exam deck', {x:1.02,y:2.35,w:5.8,h:0.3,fontSize:16,color:'334155'});
  s.addText('Stack: FastAPI + SQLAlchemy + PostgreSQL + JWT + pytest', {x:1.02,y:2.8,w:6.6,h:0.3,fontSize:18,color:'0F172A',bold:true});
  s.addText('This submission exceeds the pass criteria by combining CRUD with authentication, analytics, recommendations, testing, and deployment readiness.', {x:1.02,y:3.35,w:7.25,h:1.0,fontSize:18,color:'334155'});
  s.addShape(pptx.ShapeType.roundRect, {x:8.85,y:2.05,w:2.8,h:0.6,rectRadius:0.06,fill:{color:'DBEAFE'},line:{color:'DBEAFE'}});
  s.addText('Designed for a 5-minute demo', {x:9.1,y:2.23,w:2.3,h:0.2,fontSize:14,bold:true,color:'1D4ED8',align:'center'});
  [['Books',9.0,3.2],['Users',10.0,3.95],['Reviews',9.0,4.7],['Analytics',10.0,5.45]].forEach(([t,x,y])=>{
    s.addShape(pptx.ShapeType.roundRect,{x,y,w:1.55,h:0.5,rectRadius:0.05,fill:{color:'FFFFFF'},line:{color:'94A3B8',pt:1.2},shadow:safeOuterShadow('000000',0.12,45,1,1)});
    s.addText(t,{x:x+0.1,y:y+0.14,w:1.35,h:0.18,fontSize:14,bold:true,align:'center',color:'0F172A'});
  });
  addFooter(s,1);
}

// Slide 2
{
  const s = pptx.addSlide();
  s.background = { color: 'FFFFFF' };
  addHeader(s, 'Problem, scope, and why this topic works');
  addBulletList(s, [
    'Books are a strong relational-data domain with clear entities and relationships.',
    'The project supports CRUD, authentication, analytics, and explainable recommendations.',
    'The API is realistic enough for a technical viva but still concise enough to polish fully.',
    'The design goes beyond minimum coursework expectations by emphasising software engineering quality.'
  ], 0.7, 1.4, 6.0, 4.4);
  s.addShape(pptx.ShapeType.roundRect,{x:7.2,y:1.6,w:5.35,h:4.5,rectRadius:0.05,fill:{color:'F8FAFC'},line:{color:'CBD5E1'}});
  s.addText('Mark-winning features', {x:7.5,y:1.95,w:2.8,h:0.3,fontSize:20,bold:true,color:'0F172A'});
  const feats = [['CRUD + SQL','DCFCE7','166534'],['JWT auth','DBEAFE','1D4ED8'],['Analytics','FEF3C7','92400E'],['Tests','EDE9FE','6D28D9'],['Docs + slides','FCE7F3','9D174D']];
  feats.forEach((f,i)=>{
    const y=2.55+i*0.65;
    s.addShape(pptx.ShapeType.roundRect,{x:7.55,y,w:4.4,h:0.42,rectRadius:0.04,fill:{color:f[1]},line:{color:f[1]}});
    s.addText(f[0],{x:7.8,y:y+0.11,w:2.7,h:0.18,fontSize:15,bold:true,color:f[2]});
  });
  addFooter(s,2);
}

// Slide 3
{
  const s = pptx.addSlide();
  s.background = { color: 'FFFFFF' };
  addHeader(s, 'Architecture and database design');
  // architecture diagram
  const boxes = [
    ['Client / Swagger UI',0.8,2.0,'DBEAFE'],
    ['FastAPI Routers',3.2,2.0,'EDE9FE'],
    ['Services / Auth',5.6,2.0,'FEF3C7'],
    ['SQLAlchemy Models',8.0,2.0,'DCFCE7'],
    ['PostgreSQL',10.4,2.0,'FCE7F3']
  ];
  boxes.forEach(([t,x,y,c])=>{
    s.addShape(pptx.ShapeType.roundRect,{x,y,w:1.95,h:0.78,rectRadius:0.05,fill:{color:c},line:{color:'94A3B8'}});
    s.addText(t,{x:x+0.08,y:y+0.21,w:1.79,h:0.25,fontSize:15,bold:true,align:'center',color:'0F172A'});
  });
  [2.75,5.15,7.55,9.95].forEach(x=> s.addShape(pptx.ShapeType.chevron,{x,y:2.2,w:0.35,h:0.35,fill:{color:'94A3B8'},line:{color:'94A3B8'}}));
  s.addText('Entity relationships', {x:0.9,y:3.55,w:2.2,h:0.3,fontSize:20,bold:true,color:'0F172A'});
  // mini ERD
  [['users',1.0,4.2],['reviews',4.0,4.2],['books',7.2,4.2]].forEach(([t,x,y])=>{
    s.addShape(pptx.ShapeType.roundRect,{x,y,w:2.0,h:1.2,rectRadius:0.04,fill:{color:'F8FAFC'},line:{color:'64748B',pt:1.2}});
    s.addText(t,{x:x+0.2,y:y+0.12,w:1.6,h:0.2,fontSize:18,bold:true,align:'center',color:'0F172A'});
  });
  s.addText('id\nname\nemail\nhashed_password', {x:1.25,y:4.55,w:1.5,h:0.55,fontSize:12,align:'center',color:'334155'});
  s.addText('id\nuser_id\nbook_id\nrating\ncomment', {x:4.25,y:4.48,w:1.5,h:0.7,fontSize:12,align:'center',color:'334155'});
  s.addText('id\ntitle\nauthor\ngenre\naverage_rating', {x:7.45,y:4.48,w:1.5,h:0.7,fontSize:12,align:'center',color:'334155'});
  s.addShape(pptx.ShapeType.line,{x:3.0,y:4.8,w:1.0,h:0,line:{color:'64748B',pt:1.2,beginArrowType:'none',endArrowType:'triangle'}});
  s.addShape(pptx.ShapeType.line,{x:6.0,y:4.8,w:1.2,h:0,line:{color:'64748B',pt:1.2,beginArrowType:'none',endArrowType:'triangle'}});
  s.addText('One user can write many reviews; one book can receive many reviews.', {x:9.85,y:4.3,w:2.6,h:1.0,fontSize:16,color:'334155'});
  addFooter(s,3);
}

// Slide 4
{
  const s = pptx.addSlide();
  s.background = { color: 'FFFFFF' };
  addHeader(s, 'API endpoints and demo flow');
  s.addText('Core endpoints', {x:0.7,y:1.3,w:2.2,h:0.3,fontSize:20,bold:true,color:'0F172A'});
  const tableData = [
    [{text:'Route',options:{bold:true,color:'FFFFFF'}},{text:'Purpose',options:{bold:true,color:'FFFFFF'}}],
    ['/auth/register, /auth/login','Registration and JWT login'],
    ['/books [GET/POST]','Create and list books'],
    ['/books/{id} [GET/PUT/DELETE]','Retrieve, update, delete a book'],
    ['/reviews [POST/GET]','Authenticated review creation and listing'],
    ['/analytics/*','Aggregations and recommendations']
  ];
  s.addTable(tableData,{x:0.75,y:1.75,w:6.2,h:3.1,border:{type:'solid',pt:1,color:'CBD5E1'},fill:'FFFFFF',fontFace:'Aptos',fontSize:13,
    color:'0F172A', rowH:[0.42,0.42,0.42,0.42,0.42,0.42],
    colW:[2.7,3.5],
    autoFit:false,
    margin:0.06,
    fillRows:['0F172A','FFFFFF','F8FAFC','FFFFFF','F8FAFC','FFFFFF']});
  s.addShape(pptx.ShapeType.roundRect,{x:7.45,y:1.75,w:5.15,h:3.2,rectRadius:0.05,fill:{color:'F8FAFC'},line:{color:'CBD5E1'}});
  s.addText('Live demo sequence', {x:7.75,y:2.02,w:2.8,h:0.25,fontSize:20,bold:true,color:'0F172A'});
  addBulletList(s,[
    'Open Swagger UI and show auto-generated documentation.',
    'Create a new book record and read it back immediately.',
    'Register a user, login, and receive a bearer token.',
    'Create a review and show the book average rating update.',
    'Finish with analytics and recommendation endpoints.'
  ],7.7,2.45,4.5,2.1,16);
  s.addShape(pptx.ShapeType.roundRect,{x:7.7,y:4.55,w:4.45,h:0.55,rectRadius:0.04,fill:{color:'DBEAFE'},line:{color:'DBEAFE'}});
  s.addText('Key message: this is not just CRUD - it is a data service.', {x:7.92,y:4.73,w:4.0,h:0.18,fontSize:13.5,bold:true,color:'1D4ED8',align:'center'});
  addFooter(s,4);
}

// Slide 5
{
  const s = pptx.addSlide();
  s.background = { color: 'FFFFFF' };
  addHeader(s, 'Engineering quality: testing, version control, deployment');
  const cards = [
    ['Testing','pytest verifies auth, CRUD, analytics, and permissions.', 'DCFCE7'],
    ['Version control','Repository structure supports regular, evidence-rich commits.', 'DBEAFE'],
    ['Documentation','README, API PDF, technical report, and slides are submission-ready.', 'FEF3C7'],
    ['Deployment','Prepared for Render, Railway, or PythonAnywhere with PostgreSQL.', 'FCE7F3']
  ];
  cards.forEach((c,i)=>{
    const x = 0.85 + (i%2)*6.1;
    const y = 1.6 + Math.floor(i/2)*2.05;
    s.addShape(pptx.ShapeType.roundRect,{x,y,w:5.5,h:1.55,rectRadius:0.05,fill:{color:c[2]},line:{color:'CBD5E1'}});
    s.addText(c[0],{x:x+0.2,y:y+0.2,w:2.4,h:0.2,fontSize:19,bold:true,color:'0F172A'});
    s.addText(c[1],{x:x+0.2,y:y+0.58,w:4.9,h:0.55,fontSize:15,color:'334155'});
  });
  s.addText('Suggested oral evidence to show on screen:', {x:0.9,y:5.95,w:4.6,h:0.24,fontSize:18,bold:true,color:'0F172A'});
  addBulletList(s,[
    'GitHub commit history',
    'Swagger docs page',
    'A passing pytest run',
    'Hosted API URL or local fallback'
  ],0.95,6.25,4.5,0.7,14);
  addFooter(s,5);
}

// Slide 6
{
  const s = pptx.addSlide();
  s.background = { color: 'F8FAFC' };
  addHeader(s, 'Reflection, limitations, and future improvements');
  s.addShape(pptx.ShapeType.roundRect,{x:0.8,y:1.5,w:5.8,h:4.8,rectRadius:0.05,fill:{color:'FFFFFF'},line:{color:'CBD5E1'}});
  s.addShape(pptx.ShapeType.roundRect,{x:6.85,y:1.5,w:5.7,h:4.8,rectRadius:0.05,fill:{color:'FFFFFF'},line:{color:'CBD5E1'}});
  s.addText('What this project already demonstrates', {x:1.05,y:1.85,w:4.5,h:0.25,fontSize:20,bold:true,color:'0F172A'});
  addBulletList(s,[
    'A complete SQL-backed CRUD API',
    'Authentication and access control',
    'Analytics that create genuine added value',
    'Test evidence and submission-ready documentation'
  ],1.0,2.3,5.0,2.0,16);
  s.addText('Future work for an even stronger system', {x:7.1,y:1.85,w:4.5,h:0.25,fontSize:20,bold:true,color:'0F172A'});
  addBulletList(s,[
    'Collaborative filtering recommendations',
    'Pagination, search, and sorting',
    'Docker + CI/CD pipeline',
    'Caching and richer security controls'
  ],7.05,2.3,4.9,2.0,16);
  s.addShape(pptx.ShapeType.roundRect,{x:2.45,y:5.45,w:8.4,h:0.55,rectRadius:0.05,fill:{color:'0F172A'},line:{color:'0F172A'}});
  s.addText('Closing line: the project is deliberately scoped to be polished, defensible, and easy to demonstrate under viva conditions.', {x:2.65,y:5.62,w:7.95,h:0.18,fontSize:14,bold:true,color:'FFFFFF',align:'center'});
  addFooter(s,6);
}

pptx.writeFile({ fileName: '/mnt/data/book_api_project/slides/book_api_presentation.pptx' });
