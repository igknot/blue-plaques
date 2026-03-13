# Blue Plaques Map - Admin Guide

**⚠️ SECURITY WARNING**: The current admin system uses a hardcoded password in client-side JavaScript. This is NOT secure for production use. Implement proper server-side authentication before deploying publicly.

---

## Admin Access

### Logging In

1. Click the **hamburger menu** (☰) in the top-left corner
2. Click the **🔐 Admin Login** button
3. Enter the admin password when prompted
4. If correct, you'll see:
   - "Admin mode enabled" confirmation
   - Button changes to **🔓 Admin Mode** (green)
   - **+ button** appears in bottom-right corner

**Current Password**: `sc00by`

**⚠️ CRITICAL**: This password is visible in the page source code. Anyone can view it. Change immediately or implement proper authentication.

---

## Admin Features

### 1. Repositioning Plaques

When admin mode is enabled, all plaque markers become **draggable**.

**How to Reposition**:
1. Click and hold a plaque marker
2. Drag it to the correct location
3. Release the mouse button
4. Confirm the position update when prompted
5. The new position is saved to the database

**Use Cases**:
- Correcting GPS coordinates
- Moving markers to exact building locations
- Fixing bulk import errors

**Database Impact**:
```sql
UPDATE plaques 
SET geo_location = '{"lat": "...", "lon": "..."}' 
WHERE id = ?
```

**⚠️ Warning**: No undo feature. Position changes are immediate and permanent.
TODO log changes
---

### 2. Adding New Plaques

The **+ button** in the bottom-right corner opens the "Add New Plaque" modal.

#### Step-by-Step Process

**Step 1: Open Modal**
- Click the **+ button**
- Camera activates automatically
- Your current location is detected

**Step 2: Capture Photo**
1. Point your camera at the plaque
2. Click **📷 Capture Photo**
3. Review the captured image
4. Retake if needed (click Capture Photo again)

**Step 3: Fill Details**
- **Title**: Name of the heritage site (required)
- **Description**: Historical significance and details (required)
- **Address**: Physical location (required)
- **Categories**: Comma-separated tags (required)
  - Example: `Homes, Mansions, Architects, People`
- **Position**: Auto-detected (shown at bottom)

**Step 4: Save**
- Click **Save** to create the plaque
- Click **Cancel** to discard

**What Happens**:
1. Photo is uploaded to `static/uploads/`
2. Plaque is added to database
3. New marker appears on map immediately
4. Modal closes automatically

#### Camera Permissions

**First Time**:
- Browser will request camera permission
- Click "Allow" to enable photo capture
- Permission is remembered for future sessions

**Mobile**:
- Uses rear camera by default (better for photos)
- Switch to front camera in device settings if needed

**Troubleshooting**:
- If camera doesn't work, check browser permissions
- HTTPS required for camera access on some browsers
- Try a different browser if issues persist

#### Photo Requirements

**Current State** (⚠️ No validation):
- Any image size accepted
- No format validation
- No quality checks

**Recommended**:
- Take photos in good lighting
- Ensure plaque text is readable
- Avoid glare and shadows
- Portrait orientation works best

---

### 3. Reviewing Reported Plaques

Users can report plaques for review using the ⚠️ icon in plaque popups.

#### Finding Reported Plaques

**Current State**: No admin interface to view reports.

**Database Query**:
```sql
SELECT * FROM plaques WHERE to_review = 1;
```

**Recommended Workflow**:
1. Query database for flagged plaques
2. Review each plaque for issues
3. Make corrections (reposition, edit details)
4. Reset `to_review` flag:
   ```sql
   UPDATE plaques SET to_review = 0 WHERE id = ?;
   ```

#### Common Report Reasons

- **Incorrect Location**: Use drag-to-reposition feature
- **Wrong Information**: Edit database directly (no UI yet)
- **Broken Images**: Replace image file or update path
- **Duplicate Plaques**: Delete duplicate from database

---

## Admin Workflows

### Workflow 1: Correcting Plaque Location

**Scenario**: User reports plaque is in wrong location

1. Log in as admin
2. Search for the reported plaque
3. Click marker to verify current location
4. Drag marker to correct position
5. Confirm update
6. Mark report as resolved in database

### Workflow 2: Adding Bulk Plaques

**Scenario**: Adding multiple plaques from field visit

1. Log in as admin on mobile device
2. Navigate to first plaque location
3. Click + button
4. Capture photo
5. Fill in details
6. Save
7. Repeat for each plaque

**Tip**: Prepare plaque details in advance (titles, descriptions, categories) for faster data entry.

### Workflow 3: Verifying User Reports

**Scenario**: Multiple plaques flagged for review

1. Query database for `to_review = 1`
2. For each flagged plaque:
   - Review reported issue
   - Verify information against Heritage Portal
   - Make corrections if needed
   - Reset flag
3. Document changes in admin log

---

## Database Management

### Direct Database Access

**Location**: `blue_plaques.db` (SQLite)

**Tools**:
- SQLite Browser (GUI)
- `sqlite3` command-line tool
- Python scripts

**Common Queries**:

```sql
-- View all plaques
SELECT id, title, address, categories FROM plaques;

-- Find plaques without images
SELECT id, title FROM plaques WHERE local_image_path IS NULL;

-- Count plaques by category
SELECT categories, COUNT(*) FROM plaques GROUP BY categories;

-- Find reported plaques
SELECT id, title, address FROM plaques WHERE to_review = 1;

-- Reset all report flags
UPDATE plaques SET to_review = 0;
```

### Backup Procedures

**Before Making Changes**:
```bash
# Backup database
cp blue_plaques.db blue_plaques_backup_$(date +%Y%m%d).db

# Backup uploads folder
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz static/uploads/
```

**Restore from Backup**:
```bash
# Restore database
cp blue_plaques_backup_20260227.db blue_plaques.db

# Restore uploads
tar -xzf uploads_backup_20260227.tar.gz
```

---

## Content Guidelines

### What Qualifies as a Blue Plaque?

**Include**:
- Official heritage plaques from recognized organizations
- Sites of historical significance
- Buildings associated with notable people or events
- Verified heritage sites

**Exclude**:
- Unofficial or personal plaques
- Unverified historical claims
- Private property without permission
- Duplicate entries

### Category Standards

**Use Existing Categories**:
- Follow the Flags Trail
- Homes, Mansions
- Military, South African War
- Architects, People
- Railways
- Johannesburg Centenary
- Churches, Religious Buildings
- Schools, Educational Institutions

**Creating New Categories**:
- Use title case
- Be specific but not overly narrow
- Check for similar existing categories first
- Maintain consistency with Heritage Portal

### Description Best Practices

**Good Description**:
```
Home of Archbishop Desmond Tutu from 1975 to 1997. 
Tutu was awarded the Nobel Peace Prize in 1984 for 
his role in the struggle against apartheid. The house 
is now a museum and heritage site.
```

**Poor Description**:
```
Tutu's house. Important place.
```

**Guidelines**:
- Write 2-4 sentences
- Include dates and key facts
- Explain historical significance
- Use proper grammar and spelling
- Cite sources when possible

---

## Security Best Practices

### Current Security Issues

⚠️ **CRITICAL ISSUES**:
1. **Hardcoded Password**: Visible in page source
2. **No Server-Side Auth**: Anyone can call admin endpoints directly
3. **No Input Validation**: SQL injection and XSS risks
4. **No Rate Limiting**: Vulnerable to abuse
5. **No Audit Logging**: No record of admin actions

### Immediate Actions Required

**Before Production**:
1. **Implement Server-Side Authentication**
   - Use JWT or session-based auth
   - Store passwords securely (bcrypt)
   - Add login endpoint with rate limiting

2. **Add Authorization Checks**
   ```python
   @app.route('/api/plaques/<id>/position', methods=['PUT'])
   @require_admin  # Decorator to check auth
   def update_position(id):
       # ...
   ```

3. **Validate All Inputs**
   ```python
   from pydantic import BaseModel, validator
   
   class PlaqueUpdate(BaseModel):
       lat: float
       lon: float
       
       @validator('lat')
       def validate_lat(cls, v):
           if not -90 <= v <= 90:
               raise ValueError('Invalid latitude')
           return v
   ```

4. **Add Audit Logging**
   ```python
   logger.info(f"Admin {user_id} updated plaque {plaque_id} position")
   ```

5. **Implement Rate Limiting**
   ```python
   from flask_limiter import Limiter
   
   limiter = Limiter(app, key_func=get_remote_address)
   
   @app.route('/api/plaques', methods=['POST'])
   @limiter.limit("5 per hour")
   def add_plaque():
       # ...
   ```

### Recommended Admin Features

**User Management**:
- Multiple admin accounts
- Role-based permissions (admin, moderator, viewer)
- Activity logs per user

**Content Moderation**:
- Review queue for reported plaques
- Approval workflow for new plaques
- Bulk edit capabilities

**Analytics**:
- Track admin actions
- Monitor report trends
- Identify problematic plaques

---

## Troubleshooting

### Admin Mode Not Activating

**Problem**: Password accepted but features don't work

**Solutions**:
1. Refresh the page
2. Clear browser cache
3. Check browser console for errors
4. Verify JavaScript is enabled

### Markers Not Draggable

**Problem**: Can't reposition plaques in admin mode

**Solutions**:
1. Confirm admin mode is active (green button)
2. Try clicking marker first, then dragging
3. Check if map is fully loaded
4. Refresh page and try again

### Photo Upload Failing

**Problem**: "Failed to add plaque" error

**Solutions**:
1. Check camera permissions
2. Ensure photo was captured (preview visible)
3. Verify all required fields are filled
4. Check server logs for errors
5. Ensure `static/uploads/` directory exists and is writable

### Position Update Not Saving

**Problem**: Marker snaps back to original position

**Solutions**:
1. Check internet connection
2. Verify server is running
3. Check browser console for errors
4. Confirm database is writable
5. Check server logs

---

## API Reference for Admins

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for complete endpoint details.

**Admin Endpoints**:
- `POST /api/plaques/<id>/report` - Mark for review
- `PUT /api/plaques/<id>/position` - Update location
- `POST /api/plaques` - Add new plaque

**⚠️ Remember**: These endpoints currently have NO authentication. Use with caution.

---

## Future Admin Features

**Planned Enhancements**:
- [ ] Admin dashboard with statistics
- [ ] Review queue interface
- [ ] Bulk import/export tools
- [ ] Image management (crop, resize, replace)
- [ ] Edit plaque details (title, description, etc.)
- [ ] Delete plaques
- [ ] User management system
- [ ] Activity audit log viewer
- [ ] Automated backups
- [ ] Content approval workflow

---

## Support

### Getting Help

**Technical Issues**:
- Check server logs: `tail -f server.log`
- Check browser console: F12 → Console tab
- Review error messages carefully

**Database Issues**:
- Backup before making changes
- Use SQLite Browser for safe editing
- Test queries on backup copy first

**Contact**:
- System Administrator: [contact details]
- Technical Support: [contact details]

---

## Version History

- **v1.0** (2026-02-27): Initial admin features
  - Drag-to-reposition
  - Add new plaques
  - Report flagging

---

**Remember**: With great power comes great responsibility. Always backup before making changes, and verify information before adding new plaques.
