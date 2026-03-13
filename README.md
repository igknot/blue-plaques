# Blue Plaques Map 🏛️

Interactive web application for discovering and exploring Johannesburg's 386 heritage blue plaques.

![Version](https://img.shields.io/badge/version-1.0-blue)
![Status](https://img.shields.io/badge/status-prototype-orange)
![Security](https://img.shields.io/badge/security-needs_hardening-red)

---

## 🎯 Quick Start

```bash
# Clone repository
git clone <repository-url>
cd blue_plaques

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
export DEBUG=True  # Optional
python server.py

# Open browser
open http://localhost:5000
```

---

## 📖 What Is This?

An interactive map displaying **386 heritage blue plaques** across Johannesburg. Users can:

- 🗺️ Browse plaques on an interactive map
- 🔍 Search by title, description, or address
- 🏷️ Filter by category (Homes, Military, Churches, etc.)
- 📍 Find nearby plaques using geolocation
- 🖼️ View image galleries in full-screen lightbox
- 🔗 Link to Heritage Portal for detailed information

**Admin features** (password-protected):
- ➕ Add new plaques with camera capture
- 📌 Drag markers to correct positions
- ⚠️ Review user-reported issues

---

## 🏗️ Technology Stack

- **Backend**: Python 3.13 + Flask 3.0.3
- **Database**: SQLite (905KB)
- **Frontend**: HTML5, CSS3, JavaScript (ES6)
- **Mapping**: Leaflet.js 1.9.4
- **Tiles**: OpenStreetMap
- **Deployment**: Render.com (configured)

---

## 📚 Documentation

Comprehensive documentation created by BMAD team analysis:

| Document | Description |
|----------|-------------|
| **[PROJECT_SUMMARY.md](docs/PROJECT_SUMMARY.md)** | Complete project analysis and assessment |
| **[USER_GUIDE.md](docs/USER_GUIDE.md)** | How to use the map (for end users) |
| **[ADMIN_GUIDE.md](docs/ADMIN_GUIDE.md)** | Admin features and moderation |
| **[API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)** | Complete API reference |
| **[TECHNICAL_ARCHITECTURE.md](docs/TECHNICAL_ARCHITECTURE.md)** | System design and architecture |
| **[IMPROVEMENT_RECOMMENDATIONS.md](docs/IMPROVEMENT_RECOMMENDATIONS.md)** | Prioritized improvements |
| **[FUNCTIONAL_SPEC.md](FUNCTIONAL_SPEC.md)** | Original functional specification |
| **[URGENT_FIXES.md](URGENT_FIXES.md)** | Security fixes applied |

---

## ⚠️ Security Warning

**🚨 NOT PRODUCTION-READY 🚨**

This prototype has **critical security vulnerabilities**:

- ❌ Hardcoded admin password in client-side JavaScript
- ❌ No server-side authentication
- ❌ No input validation
- ❌ No rate limiting
- ❌ File upload vulnerabilities

**DO NOT deploy publicly without addressing these issues.**

See [IMPROVEMENT_RECOMMENDATIONS.md](docs/IMPROVEMENT_RECOMMENDATIONS.md) for detailed security fixes.

---

## 🚀 Features

### Public Features

✅ **Interactive Map**
- 386 plaque markers with tooltips
- Zoom and pan controls
- Responsive design (mobile-friendly)

✅ **Search & Filter**
- Real-time search (title, description, address)
- Category filtering with bulk actions
- Hamburger menu sidebar

✅ **Image Lightbox**
- Full-screen image viewer
- Keyboard navigation (arrows, escape)
- Image captions

✅ **Geolocation**
- "Find Near Me" button
- Blue dot marker for user location
- Auto-zoom to nearby plaques

### Admin Features

⚠️ **Requires Authentication** (currently insecure)

✅ **Add New Plaques**
- Camera capture (mobile-friendly)
- Form with title, description, address, categories
- Auto-detect GPS coordinates

✅ **Reposition Plaques**
- Drag markers to correct locations
- Confirm before saving

✅ **Review Reports**
- Users can flag plaques for review
- Admin queries database for flagged items

---

## 📊 Project Stats

- **Plaques**: 386
- **Images**: 1,157
- **Categories**: 20+
- **Database Size**: 905KB
- **API Response**: ~200KB JSON
- **Code**: 23KB HTML (monolithic)

---

## 🛠️ Development

### Project Structure

```
blue_plaques/
├── server.py              # Flask backend
├── index.html             # Frontend (monolithic)
├── favicon.svg            # App icon
├── requirements.txt       # Python dependencies
├── render.yaml           # Deployment config
├── blue_plaques.db       # SQLite database
├── static/
│   ├── images/           # 370 plaque images
│   └── uploads/          # User-uploaded images
├── docs/                 # Documentation (BMAD analysis)
│   ├── PROJECT_SUMMARY.md
│   ├── USER_GUIDE.md
│   ├── ADMIN_GUIDE.md
│   ├── API_DOCUMENTATION.md
│   ├── TECHNICAL_ARCHITECTURE.md
│   └── IMPROVEMENT_RECOMMENDATIONS.md
└── venv/                 # Python virtual environment
```

### API Endpoints

**Public**:
- `GET /` - Main application
- `GET /api/plaques` - All plaques (JSON)
- `GET /static/<path>` - Static files

**Admin** (⚠️ no auth):
- `POST /api/plaques/<id>/report` - Flag for review
- `PUT /api/plaques/<id>/position` - Update location
- `POST /api/plaques` - Add new plaque

See [API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) for details.

---

## 🧪 Testing

**Current State**: ❌ No tests

**Recommended**:
```bash
# Install test dependencies
pip install pytest playwright

# Run unit tests
pytest tests/

# Run E2E tests
playwright test
```

See [IMPROVEMENT_RECOMMENDATIONS.md](docs/IMPROVEMENT_RECOMMENDATIONS.md) for test examples.

---

## 🚢 Deployment

### Development

```bash
export DEBUG=True
python server.py
```

### Production (Current - Not Recommended)

```bash
python server.py  # Uses Flask dev server
```

### Production (Recommended)

```bash
# Install Gunicorn
pip install gunicorn

# Run with 4 workers
gunicorn -w 4 -b 0.0.0.0:5000 server:app
```

**⚠️ Before deploying**:
1. Fix security vulnerabilities
2. Set up HTTPS
3. Configure reverse proxy (Nginx)
4. Set up monitoring
5. Implement backups

See [TECHNICAL_ARCHITECTURE.md](docs/TECHNICAL_ARCHITECTURE.md) for deployment guide.

---

## 📈 Roadmap

### Phase 1: Security (Week 1) - CRITICAL

- [ ] Implement server-side authentication
- [ ] Add input validation
- [ ] Secure file uploads
- [ ] Add rate limiting

### Phase 2: UX (Week 2)

- [ ] Add loading states
- [ ] Implement empty states
- [ ] Add marker clustering
- [ ] Improve mobile experience

### Phase 3: Code Quality (Week 3)

- [ ] Split monolithic HTML
- [ ] Add unit tests
- [ ] Add E2E tests
- [ ] Set up CI/CD

### Phase 4: Performance (Week 4)

- [ ] Optimize images
- [ ] Implement caching
- [ ] Add CDN
- [ ] Load testing

### Phase 5: Features (Week 5+)

- [ ] Share links
- [ ] Advanced search
- [ ] Offline support
- [ ] User favorites

See [IMPROVEMENT_RECOMMENDATIONS.md](docs/IMPROVEMENT_RECOMMENDATIONS.md) for detailed roadmap.

---

## 🤝 Contributing

**Current State**: No contribution guidelines

**Recommended**:
1. Fork repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

See [ADMIN_GUIDE.md](docs/ADMIN_GUIDE.md) for content guidelines.

---

## 📝 License

[License information to be added]

---

## 🙏 Credits

### Data Source
- [Heritage Portal](https://heritageportal.co.za) - Plaque information and images

### Technology
- [Leaflet.js](https://leafletjs.com) - Interactive maps
- [OpenStreetMap](https://www.openstreetmap.org) - Map tiles
- [Flask](https://flask.palletsprojects.com) - Web framework

### Analysis
- **BMAD Team** - Comprehensive project analysis and documentation
  - BMad Master (Orchestration)
  - Winston (Architecture)
  - Sally (UX Design)
  - Amelia (Development)
  - Mary (Business Analysis)
  - John (Product Management)
  - Paige (Technical Writing)

---

## 📞 Support

**Issues**: Report via GitHub Issues (to be set up)  
**Questions**: [Contact information to be added]  
**Documentation**: See `docs/` folder

---

## 📊 Project Status

**Version**: 1.0 (Prototype)  
**Status**: ⚠️ Needs security hardening before production  
**Last Updated**: March 12, 2026  
**Next Milestone**: Phase 1 security improvements

---

## 🎯 Quick Links

- [View Live Demo](#) (to be deployed)
- [Report an Issue](#) (to be set up)
- [Read User Guide](docs/USER_GUIDE.md)
- [Read Admin Guide](docs/ADMIN_GUIDE.md)
- [View API Docs](docs/API_DOCUMENTATION.md)
- [See Roadmap](docs/IMPROVEMENT_RECOMMENDATIONS.md)

---

**Built with ❤️ for Johannesburg's heritage community**
