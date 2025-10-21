/** @odoo-module */

import { registry } from '@web/core/registry';
import { Component, onWillStart, useState } from '@odoo/owl';
import { useService } from '@web/core/utils/hooks';
import { _t } from '@web/core/l10n/translation';

const actionRegistry = registry.category('actions');

class SocialMediaDashboard extends Component {
    setup() {
        this.orm = useService('orm');
        this.rpc = useService('rpc');
        this.state = useState({
            accountId: null,
            accounts: [],
            metrics: [],
            posts: [],
            engagementSeries: [],
            sentimentSeries: [],
        });

        onWillStart(async () => {
            await this.loadAccounts();
            await this.loadData();
        });
    }

    async loadAccounts() {
        const accounts = await this.orm.searchRead('social.media.account', [], ['name']);
        this.state.accounts = accounts.map((acc) => ({ id: acc.id, display_name: acc.name }));
    }

    async loadData() {
        const accountId = this.state.accountId ? Number(this.state.accountId) : null;
        const [snapshotData, postData] = await Promise.all([
            this.rpc('/social_media/osint_dashboard', { account_id: accountId }),
            this.rpc('/social_media/post_performance', { account_id: accountId }),
        ]);
        this.computeMetrics(snapshotData.snapshots || []);
        this.computePosts(postData.posts || []);
    }

    computeMetrics(snapshots) {
        if (!snapshots.length) {
            this.state.metrics = [
                { label: _t('Total Reach'), value: '0' },
                { label: _t('Total Engagement'), value: '0' },
                { label: _t('Average Sentiment'), value: '0' },
            ];
            this.state.engagementSeries = [];
            this.state.sentimentSeries = [];
            return;
        }
        const totals = snapshots.reduce(
            (acc, item) => {
                acc.likes += item.likes || 0;
                acc.comments += item.comments || 0;
                acc.shares += item.shares || 0;
                acc.reach += item.reach || 0;
                acc.sentiment += item.sentiment || 0;
                return acc;
            },
            { likes: 0, comments: 0, shares: 0, reach: 0, sentiment: 0 }
        );
        const engagement = totals.likes + totals.comments + totals.shares;
        const avgSentiment = totals.sentiment / snapshots.length;
        const formatter = new Intl.NumberFormat();
        this.state.metrics = [
            { label: _t('Total Reach'), value: formatter.format(Math.round(totals.reach)) },
            { label: _t('Total Engagement'), value: formatter.format(Math.round(engagement)) },
            { label: _t('Average Sentiment'), value: avgSentiment.toFixed(2) },
        ];

        const series = snapshots.slice(-10);
        const maxEngagement = Math.max(
            1,
            ...series.map((item) => (item.likes || 0) + (item.comments || 0) + (item.shares || 0))
        );
        this.state.engagementSeries = series.map((item) => {
            const value = (item.likes || 0) + (item.comments || 0) + (item.shares || 0);
            return {
                label: this.formatDate(item.snapshot_at),
                value: formatter.format(value),
                height: Math.round((value / maxEngagement) * 100),
            };
        });

        const buckets = { positive: 0, neutral: 0, negative: 0 };
        snapshots.forEach((item) => {
            const sentiment = item.sentiment || 0;
            if (sentiment > 0.1) {
                buckets.positive += 1;
            } else if (sentiment < -0.1) {
                buckets.negative += 1;
            } else {
                buckets.neutral += 1;
            }
        });
        const maxBucket = Math.max(1, buckets.positive, buckets.neutral, buckets.negative);
        this.state.sentimentSeries = [
            {
                label: _t('Positive'),
                value: formatter.format(buckets.positive),
                width: Math.round((buckets.positive / maxBucket) * 100),
            },
            {
                label: _t('Neutral'),
                value: formatter.format(buckets.neutral),
                width: Math.round((buckets.neutral / maxBucket) * 100),
            },
            {
                label: _t('Negative'),
                value: formatter.format(buckets.negative),
                width: Math.round((buckets.negative / maxBucket) * 100),
            },
        ];
    }

    computePosts(posts) {
        const formatter = new Intl.NumberFormat();
        this.state.posts = posts.map((post) => ({
            id: post.id,
            title: post.title || _t('Untitled'),
            account: post.account || '',
            likes: formatter.format(post.likes || 0),
            comments: formatter.format(post.comments || 0),
            shares: formatter.format(post.shares || 0),
            sentiment: (post.sentiment || 0).toFixed(2),
            engagement: (post.engagement || 0).toFixed(2),
        }));
    }

    async onAccountChange(ev) {
        this.state.accountId = ev.target.value || null;
        await this.loadData();
    }

    formatDate(value) {
        if (!value) {
            return '';
        }
        try {
            return new Date(value).toLocaleDateString();
        } catch (err) {
            return value;
        }
    }
}

SocialMediaDashboard.template = 'social_media_osint_manager.dashboard';

actionRegistry.add('social_media_osint_dashboard', SocialMediaDashboard);
