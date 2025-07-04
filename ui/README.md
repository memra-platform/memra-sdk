# Memra ETL Dashboard

A modern web interface for the Memra ETL invoice processing system.

## Features

- 📁 Drag & drop PDF upload
- 🔄 Real-time ETL workflow progress tracking
- 📊 Extracted data visualization
- 🎯 Step-by-step process monitoring
- 🔐 Secure API key management

## Tech Stack

- **Frontend**: Next.js 14, React 18, TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **File Upload**: React Dropzone
- **Notifications**: React Hot Toast
- **Deployment**: Vercel

## Quick Start

### Local Development

1. **Install dependencies:**
   ```bash
   cd ui
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```

3. **Open your browser:**
   Navigate to `http://localhost:3000`

### Environment Variables

Create a `.env.local` file in the `ui` directory:

```env
NEXT_PUBLIC_MEMRA_API_URL=https://api.memra.co
```

## Deployment to Vercel

### Option 1: Vercel CLI

1. **Install Vercel CLI:**
   ```bash
   npm i -g vercel
   ```

2. **Deploy:**
   ```bash
   cd ui
   vercel
   ```

3. **Follow the prompts:**
   - Link to existing project or create new
   - Set environment variables
   - Deploy

### Option 2: GitHub Integration

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Add Memra ETL Dashboard"
   git push origin main
   ```

2. **Connect to Vercel:**
   - Go to [vercel.com](https://vercel.com)
   - Import your GitHub repository
   - Set environment variables
   - Deploy

### Option 3: Direct Upload

1. **Build the project:**
   ```bash
   cd ui
   npm run build
   ```

2. **Upload to Vercel:**
   - Go to [vercel.com](https://vercel.com)
   - Drag and drop the `ui` folder
   - Set environment variables
   - Deploy

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_MEMRA_API_URL` | Memra API endpoint | `https://api.memra.co` |

## Usage

1. **Enter your Memra API key** in the header
2. **Upload a PDF invoice** by dragging and dropping or clicking to select
3. **Click "Process Invoice"** to start the ETL workflow
4. **Monitor progress** in real-time as each step completes
5. **View extracted data** once processing is complete

## API Integration

The UI integrates with your existing Memra API:

- **File Upload**: `POST /upload`
- **ETL Processing**: Uses your existing workflow endpoints
- **Real-time Updates**: WebSocket or polling for status updates

## Customization

### Styling
- Modify `tailwind.config.js` for theme changes
- Update `app/globals.css` for custom styles

### Components
- Add new components in `components/` directory
- Update workflow steps in `app/page.tsx`

### API Integration
- Modify the `processInvoice` function in `app/page.tsx`
- Add new API endpoints as needed

## Troubleshooting

### Common Issues

1. **API Key Issues:**
   - Ensure your Memra API key is valid
   - Check API endpoint configuration

2. **File Upload Problems:**
   - Verify PDF file format
   - Check file size limits

3. **Build Errors:**
   - Run `npm install` to ensure all dependencies
   - Check TypeScript errors with `npm run lint`

### Support

For issues with the UI, check:
- Browser console for JavaScript errors
- Network tab for API request failures
- Vercel deployment logs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details 